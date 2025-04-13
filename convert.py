import ezdxf
from typing import List, Tuple, Union
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mplPolygon
import numpy as np
from pathlib import Path

from geolib.models.dstability import DStabilityModel
from geolib.geometry.one import Point
from geolib.soils.soil import Soil

from shapely.geometry import Polygon
from shapely import is_ccw


DXF_PATH = "./data"  # waar staan de tekeningen, default in een data folder onder de map van het script


def case_insensitive_glob(filepath: str, fileextension: str) -> List[Path]:
    """Find files in given path with given file extension (case insensitive)

    Arguments:
        filepath (str): path to files
        fileextension (str): file extension to use as a filter (example .gef or .csv)

    Returns:
        List(str): list of files
    """
    p = Path(filepath)
    result = []
    for filename in p.glob("**/*"):
        if str(filename.suffix).lower() == fileextension.lower():
            result.append(filename.absolute())
    return result


def generate_random_color():
    """Generates a random RGB color as a tuple."""
    return tuple(np.random.rand(3))


class DXFPoint:
    """DXF model van een punt"""

    def __init__(self, x: float, y: float):
        self.x = round(x, 2)
        self.y = round(y, 2)


class DXFPolyLine:
    """DXF model van een polylijn"""

    def __init__(self, id: str, points: List[DXFPoint]):
        self.id = id
        self.points = points

    def to_shapely(self):
        """Converteer naar een shapely polygoon"""
        return Polygon([(p.x, p.y) for p in self.points])


class DXFModel:
    """DXF model met (enkel) polygonen"""

    def __init__(self):
        self.polylines = []

    @classmethod
    def from_dxf(cls, filename: str) -> "DXFModel":
        """Genereer een DXFmodel uit een opgegeven bestand

        Args:
            filename (str): Bestand (*.dxf)

        Returns:
            DXFModel: Geeft het DXF model terug met de uitgelezen polygonen
        """
        result = DXFModel()

        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()

        # lees de polylijnen in
        for polyline in msp.query("LWPOLYLINE"):
            id = (
                polyline.dxf.handle
            )  # kan eventueel in de toekomst gebruikt worden voor herkenning van de grondsoort
            points = [DXFPoint(float(p[0]), float(p[1])) for p in polyline.vertices()]
            result.polylines.append(DXFPolyLine(id=id, points=points))

        return result

    def to_stix(self, filename: Union[Path, str]):
        """Genereer een stix bestand uit dit model

        Args:
            filename (Union[Path, str]): Naam (en eventueel pad)van het uitvoerbestand
        """
        # maak de shapely polygonen
        polygons = [p.to_shapely() for p in self.polylines]

        # genereer een DStability model met geolib
        dm = DStabilityModel()

        # voeg een standaard grondsoort toe
        soil = Soil()
        soil.name = "ongedefinieerd"
        soil.code = "ongedefinieerd"
        soil.soil_weight_parameters.saturated_weight.mean = 14.0
        soil.soil_weight_parameters.unsaturated_weight.mean = 14.0
        soil.mohr_coulomb_parameters.cohesion.mean = 2.0
        soil.mohr_coulomb_parameters.friction_angle.mean = 22.0
        _ = dm.add_soil(soil)

        # voeg te lagen toe vanuit de gevonden polygonen
        for i, poly in enumerate(polygons):
            xs, ys = poly.exterior.xy

            points = [Point(x=x, z=y) for x, y in zip(xs, ys)]

            # maak de polygonen voor de zekerheid clockwise
            if is_ccw(poly):
                points = points[::-1]

            # voeg de laag toe (hoeft niet gesloten zijn en bij shapely is het laatste punt van een polygon ook het eerste punt)
            dm.add_layer(points[:-1], soil.name)

        # sla het bestand op met de .stix extensie
        dm.serialize(Path(f"{filename}.stix"))

    def debug_plot(self, filename):
        """Genereer debug plotjes voor eventueel makkelijker debuggen van wat er mis gaat

        Args:
            filename (str): Naam die gebruikt wordt om de plotjes van de debug stappen op te slaan
        """
        # genereer de polygonen
        polygons = [p.to_shapely() for p in self.polylines]

        # maak een plotje van wat shapely van de polygonen maakt
        fig, ax = plt.subplots(figsize=(10, 10))
        for i, poly in enumerate(polygons):
            x, y = poly.exterior.xy
            patch = mplPolygon(
                list(zip(x, y)),
                facecolor=generate_random_color(),
                alpha=0.5,
                edgecolor="black",
            )
            ax.add_patch(patch)

        ax.autoscale()
        fig.savefig(f"{filename}.shapely.png")

        # maak plaatjes van elke individuele laag voor extra debug informatie
        # elke plaatje toont hoe / welke laag wordt toegevoegd
        fig, ax = plt.subplots(figsize=(10, 10))
        for i, poly in enumerate(polygons):
            xs, ys = poly.exterior.xy
            points = [Point(x=x, z=y) for x, y in zip(xs, ys)]
            if is_ccw(poly):
                points = points[::-1]

            ax.scatter([p.x for p in points], [p.z for p in points])
            ax.plot([p.x for p in points], [p.z for p in points])
            fig.savefig(f"{filename}.debug.{i:02d}.png")
        plt.close()


if __name__ == "__main__":
    # zoek naar alle dxf bestanden in het opgegeven pad
    dxf_files = case_insensitive_glob(Path(DXF_PATH), ".dxf")

    # per bestand...
    for dxf_file in dxf_files:
        print(f"Bezig met {dxf_file}...")
        filename = Path(dxf_file).stem
        try:
            # lees het bestand in naar een DXFModel
            dxf_model = DXFModel.from_dxf(dxf_file)
            # exporteer naar stix
            dxf_model.to_stix(filename=Path(DXF_PATH) / filename)
        except Exception as e:
            # als er een fout optreedt, genereer debug informatie
            dxf_model.debug_plot(filename=Path(DXF_PATH) / filename)
            # en meldt het
            print(
                f"Fout bij het converteren van '{dxf_file}'; foutmelding: '{e}', bekijk de eventueel gegenereerde afbeeldingen van het debug proces."
            )
