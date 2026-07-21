from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import hmac
import jwt
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")


# ─── Models ────────────────────────────────────────────────────────────────
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class AccessRequestCreate(BaseModel):
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None


class AccessRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmailDraftRequest(BaseModel):
    company_name: str
    industry: str
    hq: Optional[str] = None
    employees: Optional[int] = None
    stack: List[str] = []
    recent_signal: Optional[str] = None
    contact_name: str
    contact_title: str
    tone: str = "Reserved"
    sender_name: str = "Sara"


# ─── Health & Status ───────────────────────────────────────────────────────
@api_router.get("/")
async def root():
    return {"message": "Xenia"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(inp: StatusCheckCreate):
    status_obj = StatusCheck(**inp.model_dump())
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    rows = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for r in rows:
        if isinstance(r['timestamp'], str):
            r['timestamp'] = datetime.fromisoformat(r['timestamp'])
    return rows


# ─── Access Requests ───────────────────────────────────────────────────────
@api_router.post("/access", response_model=AccessRequest)
async def create_access_request(payload: AccessRequestCreate):
    email_norm = payload.email.lower().strip()
    existing = await db.access_requests.find_one({"email": email_norm}, {"_id": 0})
    if existing:
        if isinstance(existing.get('created_at'), str):
            existing['created_at'] = datetime.fromisoformat(existing['created_at'])
        return AccessRequest(**existing)
    obj = AccessRequest(email=email_norm, company=payload.company, role=payload.role)
    doc = obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.access_requests.insert_one(doc)
    return obj


@api_router.get("/access", response_model=List[AccessRequest])
async def list_access_requests():
    rows = await db.access_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    for r in rows:
        if isinstance(r.get('created_at'), str):
            r['created_at'] = datetime.fromisoformat(r['created_at'])
    return rows


# ─── AI Email Draft (Claude Sonnet 4.6 via emergentintegrations, SSE) ────
def _build_prompt(p: EmailDraftRequest) -> str:
    stack_text = ", ".join(p.stack[:4]) if p.stack else "their current stack"
    return (
        f"Write a short, high-craft cold outreach email in a {p.tone.lower()} tone. "
        f"The sender is {p.sender_name}, managing director of a modern agency using Xenia. "
        f"The recipient is {p.contact_name} ({p.contact_title}) at {p.company_name}, "
        f"a {p.industry.lower()} company"
        + (f" in {p.hq}" if p.hq else "")
        + (f" of about {p.employees} employees" if p.employees else "")
        + ". "
        + (
            f"Reference this specific recent signal: '{p.recent_signal}'. "
            if p.recent_signal
            else ""
        )
        + f"Reference their technical context: {stack_text}. "
        "Rules: no flattery, no calendar link, no attachment, no more than 130 words total. "
        "Do NOT include a subject line — email body only. "
        "One clear, low-friction ask: reply with 'send it' to receive a working-notes doc. "
        f"Sign off with just '— {p.sender_name}'."
    )


@api_router.post("/email/generate")
async def generate_email(payload: EmailDraftRequest):
    """Stream a fresh outreach draft from Claude Sonnet 4.6 as Server-Sent Events."""
    try:
        from emergentintegrations.llm.chat import (
            LlmChat,
            UserMessage,
            TextDelta,
            StreamDone,
        )
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"LLM library unavailable: {e}")

    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

    prompt = _build_prompt(payload)
    session_id = f"xenia-email-{uuid.uuid4().hex[:8]}"

    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message=(
            "You are Xenia, an AI writing outreach for a modern agency. "
            "You write like a thoughtful human — specific, referenced, restrained. "
            "You never use exclamation marks. You never write 'hope this finds you well'. "
            "Every line must reference something real about the recipient."
        ),
    ).with_model("anthropic", "claude-sonnet-4-6")

    async def event_stream():
        try:
            async for ev in chat.stream_message(UserMessage(text=prompt)):
                if isinstance(ev, TextDelta):
                    # SSE-format each token delta
                    yield f"data: {ev.content}\n\n"
                elif isinstance(ev, StreamDone):
                    yield "event: done\ndata: [DONE]\n\n"
                    break
        except Exception as e:
            logger.exception("email generation failed")
            yield f"event: error\ndata: {str(e)[:200]}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─── AI Chat (multi-turn Claude Sonnet 4.6 via emergentintegrations, SSE) ─
class ChatMessage(BaseModel):
    session_id: str
    text: str


class ChatMessageEntry(BaseModel):
    from_: str = Field(alias="from")
    text: str

    model_config = ConfigDict(populate_by_name=True)


class ChatSummariseRequest(BaseModel):
    messages: List[ChatMessageEntry]


class ChatSummariseResponse(BaseModel):
    summary: str


@api_router.post("/chat/stream")
async def chat_stream(payload: ChatMessage):
    """Stream a Claude Sonnet response for the in-OS AI Chat. Multi-turn:
    the same `session_id` accumulates conversation history inside emergentintegrations."""
    try:
        from emergentintegrations.llm.chat import (
            LlmChat,
            UserMessage,
            TextDelta,
            StreamDone,
        )
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"LLM library unavailable: {e}")

    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="text is required")

    chat = LlmChat(
        api_key=api_key,
        session_id=payload.session_id,
        system_message=(
            "You are Xenia, an AI copilot for a modern lead-gen agency. Speak in the "
            "voice of a thoughtful analyst: short paragraphs, specific, restrained. "
            "You have access to (fictional but coherent) pipeline context: 342 signals "
            "surfaced today, top companies Northlake Robotics (Series B), Orbit & Co. "
            "(ESA contract), Solstice Energy (Ørsted framework), Driftmark Logistics "
            "(new CMO), Cinder Semi (TSMC 3nm), Vessel Studio (research). Refer to "
            "these when they help, invent nothing else. Do not use exclamation marks. "
            "Do not say 'I'm an AI'. Keep replies under 90 words unless asked."
        ),
    ).with_model("anthropic", "claude-sonnet-4-6")

    async def event_stream():
        try:
            async for ev in chat.stream_message(UserMessage(text=payload.text)):
                if isinstance(ev, TextDelta):
                    yield f"data: {ev.content}\n\n"
                elif isinstance(ev, StreamDone):
                    yield "event: done\ndata: [DONE]\n\n"
                    break
        except Exception as e:
            logger.exception("chat stream failed")
            yield f"event: error\ndata: {str(e)[:200]}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@api_router.post("/chat/summarise", response_model=ChatSummariseResponse)
async def chat_summarise(payload: ChatSummariseRequest):
    """Return a one-paragraph summary of the current chat session, generated
    by Claude Sonnet in a fresh session (does not pollute the user's chat)."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"LLM library unavailable: {e}")

    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

    if not payload.messages:
        raise HTTPException(status_code=422, detail="messages is required")

    # Ignore the initial seed greeting (no user content yet)
    user_messages = [m for m in payload.messages if m.from_ == "user" and m.text.strip()]
    if not user_messages:
        raise HTTPException(status_code=422, detail="no user messages to summarise")

    transcript_lines = []
    for m in payload.messages:
        role = "User" if m.from_ == "user" else "Xenia"
        text = m.text.strip()
        if not text:
            continue
        transcript_lines.append(f"{role}: {text}")
    transcript = "\n".join(transcript_lines)

    summariser = LlmChat(
        api_key=api_key,
        session_id=f"summary-{uuid.uuid4()}",
        system_message=(
            "You are a concise executive assistant. Summarise the following "
            "conversation between a user and Xenia (an AI lead-gen copilot) as "
            "ONE short paragraph (max 3 sentences, no bullet lists, no headers). "
            "Focus on: which companies or people were discussed, what the user "
            "wants, and any next actions Xenia proposed. Use plain, direct "
            "sentences. Do not use exclamation marks. Do not begin with 'The user' "
            "or 'This conversation'."
        ),
    ).with_model("anthropic", "claude-sonnet-4-6")

    try:
        response = await summariser.send_message(
            UserMessage(text=f"Conversation transcript:\n\n{transcript}")
        )
    except Exception as e:
        logger.exception("summarise failed")
        raise HTTPException(status_code=502, detail=f"Summarisation failed: {str(e)[:200]}")

    summary = (response or "").strip()
    if not summary:
        raise HTTPException(status_code=502, detail="Empty summary from model")

    return ChatSummariseResponse(summary=summary)


# ─── Admin auth (single password → JWT) ────────────────────────────────────
JWT_ALGORITHM = "HS256"
JWT_TTL_HOURS = 24


class AdminLoginRequest(BaseModel):
    password: str


class AdminLoginResponse(BaseModel):
    token: str
    expires_at: datetime


def _create_admin_token() -> tuple[str, datetime]:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_TTL_HOURS)
    payload = {"sub": "admin", "role": "admin", "exp": exp}
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM), exp


async def require_admin(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization[7:].strip()
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
    try:
        claims = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorised")
    return claims


@api_router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(payload: AdminLoginRequest):
    expected = os.environ.get("ADMIN_PASSWORD")
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_PASSWORD not configured")
    # Constant-time comparison
    if not hmac.compare_digest(payload.password.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Incorrect password")
    token, exp = _create_admin_token()
    return AdminLoginResponse(token=token, expires_at=exp)


@api_router.get("/admin/leads", response_model=List[AccessRequest])
async def admin_leads(_: dict = Depends(require_admin)):
    rows = await db.access_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for r in rows:
        if isinstance(r.get('created_at'), str):
            r['created_at'] = datetime.fromisoformat(r['created_at'])
    return rows


# ─── App bootstrap ─────────────────────────────────────────────────────────
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
