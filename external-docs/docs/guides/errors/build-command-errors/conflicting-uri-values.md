# Error - conflicting URI values

## When it occurs

csvcubed is designed to help you create a valid self-contained cube of data as easily as possible. To help with this, it automatically creates new units, measures and code lists from the CSV that you provide. The way this works is that csvcubed extracts the distinct values from a column of the CSV input and treats these values as labels for the new code list concepts, units or measures; it then generates a URI from that label by applying the [URI-safe transformation](../../uris.md#uri-safe-transformation).

Occasionally the [URI-safe transformation](../../uris.md#uri-safe-transformation) generates concepts/units/measures with the same URI but different labels. For instance if one of your columns contains the labels `Time Period` and `Time-period`, which both map to the same URI-safe value of `time-period`, then this error will be raised.

> N.B. This error often arises due to differences in case, e.g. `Football` and `FootBall` are distinct and conflicting values which map to the same URI-safe value of `football`.

## How to fix

**csvcubed will have provided you with the label values which resulted in conflicting URIs. The labels must be altered so that the conflict no longer exists.**

Often, the conflicting labels are meant to represent the same thing but contain small errors or differences; in this case the distinct labels should be altered so that they are identical.

> e.g. `Time Period` and `Time-period` clearly represent the same concept with `Time Period` being the best label. All `Time-period` values should be corrected to read `Time Period`.

It is also possible you have two similar labels which should be distinct; if this is the case then the labels must be further differentiated such that their URI values will not conflict with one another.

> e.g. `<10` and `>=10` clearly represent different concepts but they will both be converted to URIs containing `-10`.
>
> In cases like these we suggest that you use more human-friendly labels such as `Less than 10` and `Greater than or equal to 10` or perhaps more terse equivalents such as `LT 10` and `GTE 10`.
