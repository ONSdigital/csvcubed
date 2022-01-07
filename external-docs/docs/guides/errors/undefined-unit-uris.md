# Error - undefined unit URIs

<!-- TODO: Will this be possible with info.json v2? -->

## When it occurs

The unit URIs referenced by a cube's units column do not match up with the expected unit URIs. This only happens where your cube re-uses existing unit URIs.

## How to fix

Ensure that the units column's *value URI template* is set correctly and that placing the units columns' values into the URI template generates the correct URIs as defined in the list of units.

<!-- TODO: Link to somewhere which helps the user define units. -->