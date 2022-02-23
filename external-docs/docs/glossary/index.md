# Glossary

### Dimension
The dimension components serve to identify the observations. A set of values for all the dimension components is sufficient to identify a single observation. Examples of dimensions include the time to which the observation applies, or a geographic region which the observation covers<sup>[[1]](https://www.w3.org/TR/vocab-data-cube/#cubes-model)</sup>.

### Observation
A data point which can be characterised by a dimension that defines what the data point applies to (e.g. time, area, gender) along with metadata describing what has been measured (e.g. economic activity, population), how it was measured and how the data point is expressed (e.g. units, multipliers, status)<sup>[[1]](https://www.w3.org/TR/vocab-data-cube/#cubes-model)</sup>.

### Attribute
The attribute components allow us to qualify and interpret the observed value(s). They 	enable specification of the units of measure, any scaling factors and metadata such as the 	status of the observation (e.g. estimated, provisional)<sup>[[1]](https://www.w3.org/TR/vocab-data-cube/#cubes-model)</sup>.

### Measure
The measure components represent the phenomenon being observed<sup>[[1]](https://www.w3.org/TR/vocab-data-cube/#cubes-model)</sup>.

### Unit
A quantity or increment by which something is counted or described, such as kg, mm, °C, °F, monetary units such as Euro or US dollar, simple number counts or index numbers. The unit of measure in connection with the unit multiplier, provides the level of detail for the observation value of the dimension<sup>[[3]](https://sdmx.org/wp-content/uploads/SDMX_Glossary_version_2_1-Final-2.docx)</sup>.

### Tidy Data
A format for laying out data sets. A tidy data set is arranged such that each dimension is a single column and each observation a single row. For more information, see Hadley Wickham's paper on this topic<sup>[[6]](https://www.jstatsoft.org/index.php/jss/article/view/v059i10/v59i10.pdf)</sup>.

### URI
Uniform Resource Identifier – URIs are used to name the entities and concepts so that consumers of the data can look-up those URIs to get more information, including links to other related URIs. Note that a URL (Uniform Resource Locator) is a type of URI<sup>[[2]](https://www.w3.org/TR/vocab-data-cube/#intro-rdf)</sup>.\
Examples<sup>[[11]](https://www.w3.org/TR/vocab-data-cube/#intro-rdf)</sup>:\
[http://some-uri]() \
[http://base-uri/concept-scheme/this-concept-scheme-name]() \
[cube-name.csv#dimension/some-new-dimension]() \
[ftp://ftp.is.co.za/rfc/rfc1808.txt]() \
[mailto:mduerst@ifi.unizh.ch]() \
 \
For more information, see this W3C resource<sup>[[12]](https://www.w3.org/TR/cooluris/)</sup>

### CSV-W
Comma Separated Values on the Web – a standardised format to express useful metadata about CSV files and other kinds of tabular data. For more information, see the W3C project page on this topic<sup>[[7]](https://www.w3.org/TR/tabular-data-primer/)</sup>.

### Code List
Predefined set of terms from which some statistical coded concepts take their values<sup>[[4]](https://sdmx.org/wp-content/uploads/SDMX_Glossary_version_2_1-Final-2.docx)</sup>.\
Example Code List:
| Label            | Notation       | Parent Notation | Sort Priority |
|------------------|----------------|-----------------|---------------|
| Wine             | wine           |                 | 1             |
| Made-Wine        | made-wine      |                 | 2             |
| Spirits          | spirits        |                 | 3             |
| Beer and Cider   | beer-and-cider |                 | 4             |
| Beer             | beer           |                 | 5             |

### Literal
Basic values such as strings, dates, booleans, and numbers that can only be used in the object position of an RDF triple. To allow correct parsing and interpretation, literals are best associated with a datatype<sup>[[8]](http://www.proxml.be/losd/semcubes.html)</sup>.

### Resource
Used in a general sense for whatever might be identified by a URI.  Familiar examples include an electronic document, an image, a source of information with a consistent purpose and a collection of other resources<sup>[[9]](https://datatracker.ietf.org/doc/html/rfc3986)</sup>.

### Population Characteristic
A concept to describe the set of objects that information is to be obtained about in a statistical survey. For example, the Population of adults in the Netherlands based on the Unit Type of persons<sup>[[5]](https://sdmx.org/wp-content/uploads/SDMX_Glossary_version_2_1-Final-2.docx)</sup>.

### Aggregate
An aggregate is formed when multiple numbers are gathered for statistical purposes and are expressed as one number. This could be in the form of a total or an average<sup>[[10]](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Beginners:Statistical_concept_-_Aggregate)</sup>.

## References
1. https://www.w3.org/TR/vocab-data-cube/#cubes-model
2. https://www.w3.org/TR/vocab-data-cube/#intro-rdf
3. https://sdmx.org/wp-content/uploads/SDMX_Glossary_version_2_1-Final-2.docx - Unit of measure
4. https://sdmx.org/wp-content/uploads/SDMX_Glossary_version_2_1-Final-2.docx - Codelist
5. https://sdmx.org/wp-content/uploads/SDMX_Glossary_version_2_1-Final-2.docx - Concept (b)
6. https://www.jstatsoft.org/index.php/jss/article/view/v059i10/v59i10.pdf
7. https://www.w3.org/TR/tabular-data-primer/
8. http://www.proxml.be/losd/semcubes.html
9. https://datatracker.ietf.org/doc/html/rfc3986
10. https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Beginners:Statistical_concept_-_Aggregate
11. http://www.faqs.org/rfcs/rfc2396.html
12. https://www.w3.org/TR/cooluris/
