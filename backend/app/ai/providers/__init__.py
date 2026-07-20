"""Provider interface + implementations.

The OpenAI Responses API is V1's provider *behind* this interface (AP6) —
honouring the Foundation's provider-dependency mitigation architecturally now,
cheaply, rather than contractually later, expensively. No other package
imports a provider SDK.
"""
