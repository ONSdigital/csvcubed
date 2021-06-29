from rdflib import Literal, URIRef
from typing import Annotated, Union


from sharedmodels.rdf.namespaces import RDFS
from sharedmodels.rdf.rdfresource import RdfMetadataResource, map_entity_to_uri, map_str_to_en_literal
from sharedmodels.rdf.triple import Triple, PropertyStatus
import sharedmodels.rdf.skos as skos
import sharedmodels.rdf.rdfs as rdfs
import sharedmodels.rdf.rdf as rdf


class HierarchicalCodeList(RdfMetadataResource):
    """Hierarchical Code List - Represents a generalized hierarchy of concepts which can be used for coding.
    The hierarchy is defined by one or more roots together with a property which relates concepts in the hierarchy to
    their child concept.  The same concepts may be members of multiple hierarchies provided that different
    qb:parentChildProperty values are used for each hierarchy."""
    parentChildProperty: Annotated[rdf.Property,
                                   Triple(URIRef("http://purl.org/linked-data/cube#parentChildProperty"),
                                          PropertyStatus.recommended, map_entity_to_uri)]
    """parent-child property - Specifies a property which relates a parent concept in the hierarchy to a child 
    concept."""
    def __init__(self, uri: str): 
        RdfMetadataResource.__init__(self, uri)    
        
    
class ComponentProperty(rdf.Property):
    label: Annotated[str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]
    comment: Annotated[str, Triple(RDFS.comment, PropertyStatus.mandatory, map_str_to_en_literal)]

    """Component property (abstract) - Abstract super-property of all properties representing dimensions,
    attributes or measures"""
    concept: Annotated[skos.Concept,
                       Triple(URIRef("http://purl.org/linked-data/cube#concept"),
                              PropertyStatus.recommended, map_entity_to_uri)]
    """concept - gives the concept which is being measured or indicated by a ComponentProperty"""
    def __init__(self, uri: str): 
        rdf.Property.__init__(self, uri)    
        
    
class ComponentSet(RdfMetadataResource):
    """Component set - Abstract class of things which reference one or more ComponentProperties"""
    componentProperty: Annotated[ComponentProperty,
                                 Triple(URIRef("http://purl.org/linked-data/cube#componentProperty"),
                                        PropertyStatus.recommended, map_entity_to_uri)]
    """component - indicates a ComponentProperty (i.e. attribute/dimension) expected on a DataSet, 
    or a dimension fixed in a SliceKey"""
    def __init__(self, uri: str): 
        RdfMetadataResource.__init__(self, uri)    
        
    
class Attachable(RdfMetadataResource):
    """Attachable (abstract) - Abstract superclass for everything that can have attributes and dimensions"""
    
    def __init__(self, uri: str): 
        RdfMetadataResource.__init__(self, uri)    
        
    
class AttributeProperty(ComponentProperty):
    """Attribute property - The class of components which represent attributes of observations in the cube,
    e.g. unit of measurement"""
    
    def __init__(self, uri: str): 
        ComponentProperty.__init__(self, uri)    
        
    
class SliceKey(ComponentSet):
    """Slice key - Denotes a subset of the component properties of a DataSet which are fixed in the corresponding
    slices"""
    
    def __init__(self, uri: str): 
        ComponentSet.__init__(self, uri)    
        
    
class CodedProperty(ComponentProperty):
    """Coded property - Superclass of all coded ComponentProperties"""
    codeList: Annotated[Union[skos.ConceptScheme, skos.Collection, HierarchicalCodeList],
                        Triple(URIRef("http://purl.org/linked-data/cube#codeList"),
                               PropertyStatus.recommended, map_entity_to_uri)]
    """code list - gives the code list associated with a CodedProperty"""
    def __init__(self, uri: str): 
        ComponentProperty.__init__(self, uri)    
        
    
class ComponentSpecification(ComponentSet):
    """Component specification - Used to define properties of a component (attribute, dimension etc) which are
    specific to its usage in a DSD."""
    componentRequired: Annotated[bool,
                                 Triple(URIRef("http://purl.org/linked-data/cube#componentRequired"),
                                        PropertyStatus.recommended, Literal)]
    """component required - Indicates whether a component property is required (true) or optional (false) in the 
    context of a DSD. Only applicable to components correspond to an attribute. Defaults to false (optional)."""

    order: Annotated[int, Triple(URIRef("http://purl.org/linked-data/cube#order"), PropertyStatus.recommended, Literal)]
    """order - indicates a priority order for the components of sets with this structure, used to guide presentations 
    - lower order numbers come before higher numbers, un-numbered components come last"""

    componentAttachment: Annotated[rdfs.Class,
                                   Triple(URIRef("http://purl.org/linked-data/cube#componentAttachment"),
                                          PropertyStatus.recommended, map_entity_to_uri)]
    """component attachment - Indicates the level at which the component property should be attached, this might an 
    qb:DataSet, qb:Slice or qb:Observation, or a qb:MeasureProperty."""
    def __init__(self, uri: str): 
        ComponentSet.__init__(self, uri)    
        
    
class DimensionProperty(ComponentProperty, CodedProperty):
    """Dimension property - The class of components which represent the dimensions of the cube"""
    
    def __init__(self, uri: str): 
        ComponentProperty.__init__(self, uri)
        CodedProperty.__init__(self, uri)    
        
    
class MeasureProperty(ComponentProperty):
    """Measure property - The class of components which represent the measured value of the phenomenon being observed"""
    
    def __init__(self, uri: str): 
        ComponentProperty.__init__(self, uri)    
        
    
class DataStructureDefinition(ComponentSet):
    """Data structure definition - Defines the structure of a DataSet or slice"""
    sliceKey: Annotated[SliceKey,
                        Triple(URIRef("http://purl.org/linked-data/cube#sliceKey"),
                               PropertyStatus.recommended, map_entity_to_uri)]
    """slice key - indicates a slice key which is used for slices in this dataset"""

    component: Annotated[ComponentSpecification,
                         Triple(URIRef("http://purl.org/linked-data/cube#component"),
                                PropertyStatus.recommended, map_entity_to_uri)]
    """component specification - indicates a component specification which is included in the structure of the 
    dataset"""

    def __init__(self, uri: str): 
        ComponentSet.__init__(self, uri)    
        
    
class ObservationGroup(RdfMetadataResource):
    """Observation Group - A, possibly arbitrary, group of observations."""
    observation: Annotated["Observation", Triple(URIRef("http://purl.org/linked-data/cube#observation"),
                                                 PropertyStatus.recommended, map_entity_to_uri)]
    """observation - indicates a observation contained within this slice of the data set"""
    def __init__(self, uri: str): 
        RdfMetadataResource.__init__(self, uri)    
        
    
class DataSet(Attachable):
    """Data set - Represents a collection of observations, possibly organized into various slices, conforming to some
    common dimensional structure."""
    structure: Annotated["DataStructureDefinition",
                         Triple(URIRef("http://purl.org/linked-data/cube#structure"),
                                PropertyStatus.recommended, map_entity_to_uri)]
    """structure - indicates the structure to which this data set conforms"""

    slice: Annotated["Slice",
                     Triple(URIRef("http://purl.org/linked-data/cube#slice"),
                            PropertyStatus.recommended, map_entity_to_uri)]
    """slice - Indicates a subset of a DataSet defined by fixing a subset of the dimensional values"""

    def __init__(self, uri: str): 
        Attachable.__init__(self, uri)    
        
    
class Observation(Attachable):
    """Observation - A single observation in the cube, may have one or more associated measured values"""
    dataSet: Annotated["DataSet",
                       Triple(URIRef("http://purl.org/linked-data/cube#dataSet"),
                              PropertyStatus.recommended, map_entity_to_uri)]
    """data set - indicates the data set of which this observation is a part"""
    def __init__(self, uri: str): 
        Attachable.__init__(self, uri)    
        
    
class Slice(ObservationGroup, Attachable):
    """Slice - Denotes a subset of a DataSet defined by fixing a subset of the dimensional values, component properties
     on the Slice"""
    sliceStructure: Annotated["SliceKey",
                              Triple(URIRef("http://purl.org/linked-data/cube#sliceStructure"),
                                     PropertyStatus.recommended, map_entity_to_uri)]
    """slice structure - indicates the sub-key corresponding to this slice"""
    def __init__(self, uri: str): 
        ObservationGroup.__init__(self, uri)
        Attachable.__init__(self, uri)    
