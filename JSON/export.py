"""

This file will convert JSON files downloaded from the Janelia MouseLight project
(https://www.janelia.org/project-team/mouselight) in JSON format to NeuroML2

"""

import neuroml
from neuroml import Cell
import json
import neuroml.writers as writers
from neuroml.utils import component_factory
from pyneuroml.plot.PlotMorphology import plot_2D
import sectionise




nml2_readme = "../NeuroML2/README.md"


def export_to_nml2(filename, ref, soma_diameter):

    import random

    myrandom = random.Random(123456)

    rm = open(nml2_readme)
    readme_text = rm.read()
    rm.close()

    with open(filename, "r") as json_file:
        json_info = json.load(json_file)

    print("Opened %s with info: %s" % (filename, json_info.keys()))

    net_doc = component_factory(neuroml.NeuroMLDocument, id="Net_%s" % ref)
    net = net_doc.add(neuroml.Network, id=net_doc.id, validate=False)

    planes = ["yz", "xz", "xy"]

    for n in json_info["neurons"]:

        cell_id = str(n["idString"])
        print("============================\nLooking at neuron id: %s" % (cell_id))
        cell_doc = component_factory(
            neuroml.NeuroMLDocument, id=cell_id
        )  # type: neuroml.NeuroMLDocument
        cell = None
        cell = cell_doc.add(Cell, id=cell_id)  # type: neuroml.Cell
        cell.morphology.id = f"morph_{cell_id}"
        # cell.morphology.info(show_contents=True)

        notes = (
            """\n    Cell %s downloaded from Janelia MouseLight project (https://www.janelia.org/project-team/mouselight)\n    and converted to NeuroML"""
            % cell_id
        )
        notes += "\n    DOI of original cell: https://doi.org/%s" % n["DOI"]
        notes += (
            "\n\n    NOTE: cells have been given a soma of diameter %sum for visualisation purposes"
            % soma_diameter
        )
        notes += "\n    However, no soma has been reconstructed from the original cells"

        cell.notes = notes

        # various properties
        for k in [
            "idString",
            "DOI",
            "sample/date",
            "sample/strain",
            "label/virus",
            "label/fluorophore",
        ]:

            if "/" in k:
                k1 = k.split("/")[0]
                k2 = k.split("/")[1]
                p = neuroml.Property(
                    tag="JaneliaMouseLight:%s_%s" % (k1, k2), value=n[k1][k2]
                )
            else:
                p = neuroml.Property(tag="JaneliaMouseLight:%s" % k, value=n[k])

            cell.add(p)

        # network and population to hold the cell
        net_doc.add(neuroml.IncludeType, href=cell.id + ".cell.nml")
        pop = net.add(
            neuroml.Population,
            id="pop_" + cell.id,
            component=cell.id,
            type="populationList",
        )
        pop.add(
            neuroml.Property,
            tag="color",
            value="%s %s %s"
            % (myrandom.random(), myrandom.random(), myrandom.random()),
        )
        pop.add(neuroml.Instance, id="0", location=neuroml.Location(x=0, y=0, z=0))

        # morphology
        id_vs_seg = {}

        # soma
        soma = cell.add_segment(
            prox=[
                float(n["soma"]["x"]),
                float(n["soma"]["y"]),
                float(n["soma"]["z"]),
                soma_diameter,
            ],
            dist=[
                float(n["soma"]["x"]),
                float(n["soma"]["y"]),
                float(n["soma"]["z"]),
                soma_diameter,
            ],
            name="soma",
            group_id=None,
            seg_type="soma"
        )
        # first segment, so its ID will be 0
        id_vs_seg[0] = soma

        # axon and dendrites
        last_seg_id = -2
        offsets = {"axon": 1000, "dendrite": 1000000}
        for sg in offsets.keys():

            # add_segment checks for `dend_`
            group = "dend" if sg == "dendrite" else "axon"
            # initialise

            for a in n[sg]:
                sg_id = int(a["sampleNumber"]) + offsets[sg]
                # print(f"processing {sg_id}")
                parent = int(a["parentNumber"])
                proximal = None
                distal = [
                    float(a["x"]),
                    float(a["y"]),
                    float(a["z"]),
                    float(a["radius"]) * 2,
                ]
                # parent == -1, soma is parent
                if parent == -1:
                    parent = 0
                else:
                    # calculate ID of parent
                    parent += offsets[sg]

                # set the parent
                seg_parent = id_vs_seg[parent]

                # proximal is required if the parent is not in the same segment
                # group
                # we set proximal for all segments

                # if soma is the parent:
                # - set proximal of this segment as distal of soma, but use
                # single diameter value
                if parent == 0:
                    proximal = [
                        seg_parent.distal.x,
                        seg_parent.distal.y,
                        seg_parent.distal.z,
                        distal[3],
                    ]
                else:
                    proximal = [
                        seg_parent.distal.x,
                        seg_parent.distal.y,
                        seg_parent.distal.z,
                        seg_parent.distal.diameter,
                    ]

                # also adds to the `all` group
                seg = cell.add_segment(
                    prox=proximal,
                    dist=distal,
                    seg_id=f"{sg_id}",
                    name=f"{group}_{sg_id}",
                    group_id=None,
                    parent=seg_parent,
                    use_convention=True,
                    seg_type=sg,
                    reorder_segment_groups=False,
                )

                # override ID to use offset based ID
                seg.id = sg_id

                # track the current segment id for the next segment
                last_seg_id = sg_id
                # add current segment to id vs segment map
                id_vs_seg[sg_id] = seg

        sectionise.sectionise(cell, 0)
        cell.reorder_segment_groups()
        cell.validate(recursive=True)
        cell.summary()
        nml_file = "../NeuroML2/%s.cell.nml" % cell.id

        writers.NeuroMLWriter.write(cell_doc, nml_file)
        print("Saved cell file to: " + nml_file)

        if not n["DOI"] in readme_text:
            readme_text += "\n\n## %s" % (cell_id,)
            height = 200

            readme_text += "\n<p>"
            for plane in planes:
                readme_text += (
                    '<img src="images/%s.cell.%s.png" alt="%s_%s" height="%s"/> '
                    % (cell_id, plane, cell_id, plane, height)
                )
            readme_text += "</p>"

            readme_text += "\nCell with %i segments (soma: %i dend: %i, axon %i)" % (
                len(cell.morphology.segments),
                len(cell.get_segment_group("soma_group").members),
                len(cell.get_segment_group("dendrite_group").members),
                len(cell.get_segment_group("axon_group").members),
            )
            readme_text += (
                "\n\n"
                + ("https://doi.org/%s" % n["DOI"] if n["DOI"] != "n/a" else "No DOI")
                + ' - <a href="%s.cell.nml">NeuroML file</a>' % (cell_id)
            )

        print(f"Generating morphology graphs for {cell.id}")
        for plane in planes:
            p2d_file = "../NeuroML2/images/%s.cell.%s.png" % (cell.id, plane)
            gen_png = False
            if gen_png:
                plot_2D(
                    nml_file,
                    plane2d=plane,
                    min_width=0,
                    verbose=False,
                    nogui=True,
                    save_to_file=p2d_file,
                    square=True,
                )

    nml_file = "../NeuroML2/%s.net.nml" % net.id
    writers.NeuroMLWriter.write(net_doc, nml_file)
    print("Saved network file to: " + nml_file)

    rm = open(nml2_readme, "w")
    rm.write(readme_text)
    rm.close()

    print("Saved README to: " + nml2_readme)


if __name__ == "__main__":

    files = {
        "MOp": "MOp.json",
        "AA0052": "AA0052.json",
        "Hippocampal": "mlnb-export.json",
        "AA1506": "AA1506.json",
        "AA1507": "AA1507.json",
    }
    # files = {'AA0052': 'AA0052.json'}
    # files = {'MOp2':'MOp2.json'}
    # files = {'AA1506':'AA1506.json','AA1507':'AA1507.json'}

    for f in files:
        export_to_nml2(files[f], f, soma_diameter=20)
