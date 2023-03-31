# Error - Only 1 primary key is supported but detected `y` primary keys for the table with URL `z`

## When it occurs

The table contains a composite primary key (i.e. a primary key with more than one column).

## How to fix

Make sure that the tables only contains primary keys with one column.
