import neuroml

import neuroml.loaders as loaders
import neuroml.writers as writers


def create_active_cell(cell_id):

    fn = "../%s.cell.nml" % cell_id
    doc = loaders.NeuroMLLoader.load(fn)
    print("Loaded morphology file from: " + fn)

    cell = doc.cells[0]  # type: neuroml.Cell
    cell.summary()
    cell.info(show_contents=True)

    # set up cell with default components
    # note: will not overwrite any pre-existing components
    cell.setup_nml_cell(use_convention=False)
    cell.info(show_contents=True)

    nml_doc2 = neuroml.NeuroMLDocument(id=cell.id)
    nml_doc2.add(cell)

    cell.add_channel_density(
        nml_cell_doc=nml_doc2,
        cd_id="pas_chan",
        ion_channel="pas",
        cond_density="0.000142857 S_per_cm2",
        erev="-70.0 mV",
        group="all",
        ion="non_specific",
        ion_chan_def_file="pas.channel.nml",
    )

    cell.add_channel_density(
        nml_cell_doc=nml_doc2,
        cd_id="na_chan",
        group="all",
        ion="na",
        ion_channel="na",
        erev="60.0 mV",
        cond_density="0.1 S_per_cm2",
        ion_chan_def_file="na.channel.nml",
    )

    cell.add_channel_density(
        nml_cell_doc=nml_doc2,
        cd_id="kv_chan",
        group="all",
        ion="k",
        ion_channel="kv",
        erev="-90.0 mV",
        cond_density="0.01 S_per_cm2",
        ion_chan_def_file="kv.channel.nml",
    )

    cell.set_specific_capacitance("1.0 uF_per_cm2", group="all")
    cell.set_init_memb_potential("-80 mV", group="all")

    # Intracellular Properties
    cell.set_resistivity("100 ohm_cm", group="all")

    cell.id = "%s" % cell_id

    # validate
    cell.validate(recursive=True)

    nml_file = cell.id + "_active.cell.nml"
    writers.NeuroMLWriter.write(nml_doc2, nml_file)

    print("Saved modified morphology file to: " + nml_file)


if __name__ == "__main__":

    cells = {"AA0173", "AA0289", "AA1506", "AA1507"}
    for cell_id in cells:
        create_active_cell(cell_id)
