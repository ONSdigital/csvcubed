# Linking units

This page introduces some of the *units of measure* that you can use to describe your data. It assumes that you have a rough understanding of what linked data is and where you might want to make use of it.

If you already know which unit you want to reuse but want to find out how to use it, see the guide on [reusing units](../configuration/units.md#linking-a-new-unit-to-an-existing-unit).

## QUDT

[QUDT's Units Vocabulary](http://www.qudt.org/doc/DOC_VOCAB-UNITS.html#Instances) is the preferred system of units recommended for use with csvcubed.

Below we list a summary of some of the key units you may wish to use. Note that the units listed in this document **are not exhaustive**; if the unit that you want to represent has not been listed below then please refer to [QUDT's Units Vocabulary](http://www.qudt.org/doc/DOC_VOCAB-UNITS.html#Instances) to see if a suitable unit has already been published. If not, you may wish to [define a new unit](../configuration/units.md#defining-a-new-unit).

## Currencies

>e.g. average household income in a given region.

| Unit           | Identifier                                 |                                           Quantity Kind |
|:---------------|:-------------------------------------------|--------------------------------------------------------:|
| Pound Sterling | <http://qudt.org/vocab/unit/PoundSterling> | [Currency](http://qudt.org/vocab/quantitykind/Currency) |
| Euro           | <http://qudt.org/vocab/unit/Euro>          | [Currency](http://qudt.org/vocab/quantitykind/Currency) |
| US Dollar      | <http://qudt.org/vocab/unit/USDollar>      | [Currency](http://qudt.org/vocab/quantitykind/Currency) |

## Lengths

>e.g. distance from population centres to the nearest train station.

| Unit  | Identifier                      |                                       Quantity Kind |
|:------|:--------------------------------|----------------------------------------------------:|
| Metre | <http://qudt.org/vocab/unit/M>  | [Length](http://qudt.org/vocab/quantitykind/Length) |
| Yard  | <http://qudt.org/vocab/unit/YD> | [Length](http://qudt.org/vocab/quantitykind/Length) |
| Mile  | <http://qudt.org/vocab/unit/MI> | [Length](http://qudt.org/vocab/quantitykind/Length) |

## Areas

>e.g. Area of green space in a given locality.

| Unit         | Identifier                       |                                   Quantity Kind |
|:-------------|:---------------------------------|------------------------------------------------:|
| Square inch  | <http://qudt.org/vocab/unit/IN2> | [Area](http://qudt.org/vocab/quantitykind/Area) |
| Square metre | <http://qudt.org/vocab/unit/M2>  | [Area](http://qudt.org/vocab/quantitykind/Area) |
| Acre         | <http://qudt.org/vocab/unit/AC>  | [Area](http://qudt.org/vocab/quantitykind/Area) |
| Hectare      | <http://qudt.org/vocab/unit/HA>  | [Area](http://qudt.org/vocab/quantitykind/Area) |

## Volumes

>e.g. volume of potholes on roads in a given area.

| Unit                   | Identifier                              |                                       Quantity Kind |
|:-----------------------|:----------------------------------------|----------------------------------------------------:|
| Litre                  | <http://qudt.org/vocab/unit/L>          | [Volume](http://qudt.org/vocab/quantitykind/Volume) |
| Cubic metre            | <http://qudt.org/vocab/unit/M3>         | [Volume](http://qudt.org/vocab/quantitykind/Volume) |
| Pint (UK)              | <http://qudt.org/vocab/unit/PINT_UK>    | [Volume](http://qudt.org/vocab/quantitykind/Volume) |
| Teaspoon               | <http://qudt.org/vocab/unit/TSP>        | [Volume](http://qudt.org/vocab/quantitykind/Volume) |
| Tablespoon             | <http://qudt.org/vocab/unit/TBSP>       | [Volume](http://qudt.org/vocab/quantitykind/Volume) |
| Barrels (UK Petroleum) | <http://qudt.org/vocab/unit/BBL_UK_PET> | [Volume](http://qudt.org/vocab/quantitykind/Volume) |

## Time Periods

>e.g. how long it takes an athlete to complete a 100m sprint.

| Unit    | Identifier                       |                                   Quantity Kind |
|:--------|:---------------------------------|------------------------------------------------:|
| Seconds | <http://qudt.org/vocab/unit/SEC> | [Time](http://qudt.org/vocab/quantitykind/Time) |
| Minutes | <http://qudt.org/vocab/unit/MIN> | [Time](http://qudt.org/vocab/quantitykind/Time) |
| Hours   | <http://qudt.org/vocab/unit/HR>  | [Time](http://qudt.org/vocab/quantitykind/Time) |
| Days    | <http://qudt.org/vocab/unit/DAY> | [Time](http://qudt.org/vocab/quantitykind/Time) |
| Years   | <http://qudt.org/vocab/unit/YR>  | [Time](http://qudt.org/vocab/quantitykind/Time) |

## Counts & rates

>e.g. the number of people observed sleeping rough in town centres on a given night.

| Unit            | Identifier                              |                                                     Quantity Kind |
|:----------------|:----------------------------------------|------------------------------------------------------------------:|
| Number (count)  | <http://qudt.org/vocab/unit/NUM>        | [Dimensionless](http://qudt.org/vocab/quantitykind/Dimensionless) |
| Per day         | <http://qudt.org/vocab/unit/PER-DAY>    |         [Frequency](http://qudt.org/vocab/quantitykind/Frequency) |
| Number per hour | <http://qudt.org/vocab/unit/NUM-PER-HR> |         [Frequency](http://qudt.org/vocab/quantitykind/Frequency) |
| Hz              | <http://qudt.org/vocab/unit/HZ>         |         [Frequency](http://qudt.org/vocab/quantitykind/Frequency) |

## Energies

>e.g. electrical energy consumption of households on a given day.

| Unit        | Identifier                            |                                       Quantity Kind |
|:------------|:--------------------------------------|----------------------------------------------------:|
| kWh         | <http://qudt.org/vocab/unit/KiloW-HR> | [Energy](http://qudt.org/vocab/quantitykind/Energy) |
| Kilocalorie | <http://qudt.org/vocab/unit/KiloCAL>  | [Energy](http://qudt.org/vocab/quantitykind/Energy) |

## Temperatures

>e.g. daily observed maximum/minimum air temperatures.

| Unit            | Identifier                         |                                                 Quantity Kind |
|:----------------|:-----------------------------------|--------------------------------------------------------------:|
| Degrees Celcius | <http://qudt.org/vocab/unit/DEG_C> | [Temperature](http://qudt.org/vocab/quantitykind/Temperature) |
| Degrees Kelvin  | <http://qudt.org/vocab/unit/K>     | [Temperature](http://qudt.org/vocab/quantitykind/Temperature) |

## Weights

>e.g. weights of new-born babies.

| Unit              | Identifier                              |                                   Quantity Kind |
|:------------------|:----------------------------------------|------------------------------------------------:|
| Kilogramme        | <http://qudt.org/vocab/unit/KiloGM>     | [Mass](http://qudt.org/vocab/quantitykind/Mass) |
| Metric Tonne      | <http://qudt.org/vocab/unit/TON_Metric> | [Mass](http://qudt.org/vocab/quantitykind/Mass) |
| Imperial Ton (UK) | <http://qudt.org/vocab/unit/TON_UK>     | [Mass](http://qudt.org/vocab/quantitykind/Mass) |
| Stone             | <http://qudt.org/vocab/unit/Stone_UK>   | [Mass](http://qudt.org/vocab/quantitykind/Mass) |

## Ranks and ordinals

>e.g. the ranks/final positions of participants in a competition.

Occasionally you may want to record the ranks or ordinals. Ranks do not  have a unit and so you should express this with the [UNITLESS](http://qudt.org/vocab/unit/UNITLESS) *unit*.

| Unit     | Identifier                            |                                                     Quantity Kind |
|:---------|:--------------------------------------|------------------------------------------------------------------:|
| Unitless | <http://qudt.org/vocab/unit/UNITLESS> | [Dimensionless](http://qudt.org/vocab/quantitykind/Dimensionless) |
