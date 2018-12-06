import neuroml

import neuroml.loaders as loaders
import neuroml.writers as writers

def create_active_cell(cell_id):

    fn = '../%s.cell.nml'%cell_id
    doc = loaders.NeuroMLLoader.load(fn)
    print("Loaded morphology file from: "+fn)

    cell = doc.cells[0]


    channel_densities = []

    cd_pas = neuroml.ChannelDensity(id="pas_chan", segment_groups="all", ion="non_specific", ion_channel="pas", erev="-70.0 mV", cond_density="0.000142857 S_per_cm2")
    channel_densities.append(cd_pas)
    
    cd_na = neuroml.ChannelDensity(id="na_chan", segment_groups="all", ion="na", ion_channel="na", erev="60.0 mV", cond_density="0.1 S_per_cm2")
    channel_densities.append(cd_na)
    
    cd_kv = neuroml.ChannelDensity(id="kv_chan", segment_groups="all", ion="k", ion_channel="kv", erev="-90.0 mV", cond_density="0.01 S_per_cm2")
    channel_densities.append(cd_kv)



    specific_capacitances = []

    specific_capacitances.append(neuroml.SpecificCapacitance(value='1.0 uF_per_cm2',
                                                segment_groups='all'))

    init_memb_potentials = [neuroml.InitMembPotential(
        value="-80 mV", segment_groups='all')]

    membrane_properties = neuroml.MembraneProperties(
        channel_densities=channel_densities,
        specific_capacitances=specific_capacitances,
        init_memb_potentials=init_memb_potentials)

    # Intracellular Properties
    #
    resistivities = []
    resistivities.append(neuroml.Resistivity(
        value="100 ohm_cm", segment_groups='all'))

    intracellular_properties = neuroml.IntracellularProperties(resistivities=resistivities)

    bp = neuroml.BiophysicalProperties(id="biophys",
                                       intracellular_properties=intracellular_properties,
                                       membrane_properties=membrane_properties)

    cell.biophysical_properties = bp

    cell.id = '%s'%cell_id

    nml_doc2 = neuroml.NeuroMLDocument(id=cell.id)

    nml_doc2.includes.append(neuroml.IncludeType('pas.channel.nml')) 
    nml_doc2.includes.append(neuroml.IncludeType('na.channel.nml')) 
    nml_doc2.includes.append(neuroml.IncludeType('kv.channel.nml')) 
    #nml_doc2.includes.append(neuroml.IncludeType('channelConvert/Na_BC.channel.nml')) 
    #nml_doc2.includes.append(neuroml.IncludeType('channelConvert/K_BC.channel.nml')) 
    nml_doc2.cells.append(cell)

    nml_file = cell.id+'_active.cell.nml'

    writers.NeuroMLWriter.write(nml_doc2,nml_file)

    print("Saved modified morphology file to: "+nml_file)


    ###### Validate the NeuroML ######    

    from neuroml.utils import validate_neuroml2

    validate_neuroml2(nml_file)


if __name__ == "__main__":
    
    cells = {'AA0173'}
    for cell_id in cells:
        create_active_cell(cell_id)
    
    