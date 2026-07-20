# features/

Organised by product concept (Doc 08 §4): each feature owns its routes, hooks,
and components, and is the unit of ownership *and of deletion* — a cut feature
is a deleted folder, not an archaeology project.

No business logic lives here (AP5): features render state and collect intent;
rules arrive from the API as data.
