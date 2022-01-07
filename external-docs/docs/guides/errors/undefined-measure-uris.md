# Error - undefined measure URIs

<!-- TODO: Will this be possible with info.json v2? -->

## When it occurs

The measure URIs referenced by a cube's measure dimension do not match up with the expected measure URIs. This only happens where your cube re-uses existing measure URIs.

## How to fix

Ensure that the measure column's *value URI template* is set correctly and that placing the measure columns' values into the URI template generates the correct URIs as defined in the list of measures.

<!-- TODO: Link to somewhere which helps the user define measures. -->