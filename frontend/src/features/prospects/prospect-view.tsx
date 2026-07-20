/** One prospect: the brief one click deep, the outcome one tap away. */
import { BriefView } from "@/features/brief/brief-view";
import { OutcomeForm } from "@/features/outcomes/outcome-form";
import { DraftPanel } from "@/features/prospects/draft-panel";

export function ProspectView({ prospectId }: { prospectId: string }) {
  return (
    <div>
      <BriefView prospectId={prospectId} />
      <DraftPanel prospectId={prospectId} />
      <OutcomeForm prospectId={prospectId} />
    </div>
  );
}
