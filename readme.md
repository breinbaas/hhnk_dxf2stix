# DXF naar STIX

Dit script converteert DXF bestanden die binnen HHNK gemaakt worden naar Deltares DStability (stix) bestanden.

![Voorbeeld](https://github.com/breinbaas/hhnk_dxf2stix/blob/master/img/sample.jpg)

## DXF eisen 

Alle lagen dienen als polygonen gedefinieerd te zijn. Alle lijnen van de polygonen dienen aaneengesloten te zijn en bij meerdere lagen dienen gedeelde punten op beide lagen voor te komen.

## Installatie

Download de code van het script via;
* git clone ```git@github.com:breinbaas/hhnk_dxf2stix.git```
* ga naar de directory met de code en maak een virtuele omgeving aan; ```python -m venv .venv```
* installeer de benodigde packages ```python -m pip install -r requirements.txt```

## Script uitvoeren
* activeer de virtuele omgeving ```.venv/scripts/activate```
* plaats de DXF bestanden in de de ```/data``` directory 
* run het script ```python convert.py```
* in de data directory worden stix bestanden gegenereerd met dezelfde naam als het dxf bestand maar met ```stix``` als extensie

## Debug informatie

Indien er fouten optreden bij de conversie van een DXF bestand wordt geprobeerd om afbeeldingen van het conversie proces te genereren. Deze verschijnen in het uitvoerpad met de naam <filename>.debug.<stap>.png

Op deze manier kan eenvoudiger bepaald worden of er in de DXF fouten zitten.

