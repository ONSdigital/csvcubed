from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List





class ValidatedModel(DataClassModelBase, ABC):

    def validate(self) -> List[ValidationErrors]:
        pass
     #some implementation goes here which makes a call to self._get_validations() and then executes the validations

    @abstractmethod
    def _get_validations(self) -> Dict[str, Callable[[Any], List[ValidationErrors]]]:
        pass

    @abstractmethod
    def ensure_str(self):
        pass
    @abstractmethod
    def ensure_positive_integer_or_none(self):
        pass    


    
    

@dataclass
class SomeModel(ValidatedModel):

    self.some_property: str
    self.some_child_data_class: SomeOtherValidatedModel
    self.some_optional_property: Optional[int] = field(default=None)

    def _get_validations(self) -> Dict[str, Callable[[Any], List[ValidationErrors]]]:
     return {
        "some_property": ensure_str(),
        "some_optional_property": ensure_positive_integer_or_none(),
        "some_optional_property": lambda v: v.validate()  # Recursively calls the validation function on the other validated model.
    }

    def _validate_some_property(self) -> List[ValidationError]:
        if isinstance(str, self.some_property):
            pass



def main():
    pass



if __name__ == "__main__":
    main()