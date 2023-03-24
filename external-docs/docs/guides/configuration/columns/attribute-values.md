# Attribute values configuration

This page discusses what attribute values are, where they should be used, and how they can be defined.

> For a detailed look at attribute values configuration options, see the [Reference table](#reference) at the
bottom of this page.

This section will focus on defining new Resource attributes through configuration of the attribute column's `values`
field, and their presence in the structure of a cube configuration file. Details of attribute values configuration
options can be found in the [Reference table](#reference) at the bottom of this page.

## Reference

| **field name**   | **description**                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------|-------------------|
| `label`          | The title of the attribute (Required; Optional if `from_existing` defined)  | *none*            |
| `description`    | A description of the contents of the attribute (Optional)                   | *none*            |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                      | *none*            |
| `definition_uri` | A uri of a resource to show how the attribute is created/managed (Optional) | *none*            |
