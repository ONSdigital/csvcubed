"""
Models
------

info.json V1.1 column mapping models.
"""
from dataclasses import dataclass, fields, Field
from typing import Any, List, Union, Optional, Type, TypeVar


T = TypeVar("T", bound=object)


def _from_dict(cls: Type[T], d: dict) -> T:
    instance = cls()
    for field in fields(instance):
        assert isinstance(field, Field)
        if field.name in d.keys():
            setattr(instance, field.name, d[field.name])


@dataclass
class NewDimensionProperty:
    codelist: Union[str, False]
    path: Optional[str] = None
    label: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None
    subPropertyOf: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewDimensionProperty":
        return _from_dict(cls, d)


@dataclass
class NewDimension:
    new: Union[NewDimensionProperty, True]
    value: Optional[str]

    @classmethod
    def from_dict(cls, d: dict) -> "NewDimensionProperty":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.new = NewDimensionProperty.from_dict(instance.new)
        return instance


@dataclass
class ExistingDimension:
    uri: str
    value: str

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingDimension":
        return _from_dict(cls, d)


@dataclass
class NewAttributeValue:
    label: str
    path: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "NewAttributeValue":
        return _from_dict(cls, d)


@dataclass
class NewAttributeProperty:
    path: Optional[str] = None
    label: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None
    subPropertyOf: Optional[str] = None
    newAttributeValues: Union[None, True, List[NewAttributeValue]] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingDimension":
        instance = _from_dict(cls, d)
        if isinstance(instance.newAttributeValues, list):
            instance.newAttributeValues = [
                NewDimensionProperty.from_dict(attr_val)
                for attr_val in instance.newAttributeValues
            ]
        return instance


@dataclass
class NewAttribute:
    new: Union[True, NewAttributeProperty]
    isRequired: Optional[bool] = True

    @classmethod
    def from_dict(cls, d: dict) -> "NewAttribute":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.new = NewAttributeProperty.from_dict(instance.new)
        return instance


@dataclass
class ExistingAttribute:
    uri: str
    value: Optional[str] = None
    newAttributeValues: Union[None, True, List[NewAttributeValue]] = None
    isRequired: Optional[bool] = True

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingAttribute":
        instance = _from_dict(cls, d)
        if isinstance(instance.newAttributeValues, list):
            instance.newAttributeValues = [
                NewAttributeValue.from_dict(attr_val)
                for attr_val in instance.newAttributeValues
            ]
        return instance


@dataclass
class Resource:
    label: str
    path: Optional[str] = None
    comment: Optional[str] = None
    isDefinedBy: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Resource":
        return _from_dict(cls, d)


@dataclass
class NewUnits:
    new: Union[True, List[Resource]]

    @classmethod
    def from_dict(cls, d: dict) -> "NewUnits":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, list):
            instance.new = [Resource.from_dict(attr_val) for attr_val in instance.new]
        return instance


@dataclass
class ExistingUnits:
    value: str

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingUnits":
        return _from_dict(cls, d)


@dataclass
class NewMeasures:
    new: Union[True, List[Resource]]

    @classmethod
    def from_dict(cls, d: dict) -> "NewMeasures":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, list):
            instance.new = [Resource.from_dict(attr_val) for attr_val in instance.new]
        return instance


@dataclass
class ExistingMeasures:
    value: str

    @classmethod
    def from_dict(cls, d: dict) -> "ExistingMeasures":
        return _from_dict(cls, d)


@dataclass
class ObservationValue:
    datatype: Optional[str]
    unit: Union[None, str, Resource] = None
    measure: Union[None, str, Resource] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ObservationValue":
        instance = _from_dict(cls, d)
        if isinstance(instance.new, dict):
            instance.unit = Resource.from_dict(instance.unit)
        if isinstance(instance.measure, dict):
            instance.measure = Resource.from_dict(instance.measure)

        return instance
