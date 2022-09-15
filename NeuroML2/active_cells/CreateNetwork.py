
import neuroml

import neuroml.loaders as loaders
import neuroml.writers as writers

from pyneuroml.lems import generate_lems_file_for_neuroml

import sys
import os

def get_pop_id(cell_id):
    return "Pop_%s"%cell_id

def create_network_for_cells(cell_ids, net_id, stim_amp='450pA'):

    net_doc = neuroml.NeuroMLDocument(id=net_id)

    net = neuroml.Network(id=net_id)
    net_doc.networks.append(net)

    for cell_id in cell_ids:
        cell_file = cell_id+'_active.cell.nml'
        net_doc.includes.append(neuroml.IncludeType(cell_file))

        pop = neuroml.Population(id=get_pop_id(cell_id),
                    component=cell_id,
                    type="populationList")

        inst = neuroml.Instance(id="0")
        pop.instances.append(inst)
        inst.location = neuroml.Location(x=0, y=0, z=0)
        net.populations.append(pop)

        stim = neuroml.PulseGenerator(id='stim_%s'%cell_id,
                                     delay='20ms',
                                     duration='300ms',
                                     amplitude=stim_amp)

        net_doc.pulse_generators.append(stim)


        input_list = neuroml.InputList(id="%s_input"%stim.id,
                                       component=stim.id,
                                       populations=pop.id)

        syn_input = neuroml.Input(id=0,
                                  target="../%s/0/%s" % (pop.id, pop.component),
                                  destination="synapses")

        input_list.input.append(syn_input)
        net.input_lists.append(input_list)



    nml_file = net.id+'.net.nml'

    writers.NeuroMLWriter.write(net_doc,nml_file)

    print("Saved network file to: "+nml_file)


    ###### Validate the NeuroML ######

    from neuroml.utils import validate_neuroml2

    validate_neuroml2(nml_file)

    sim_id = 'Test_%s'%net_id
    target = net.id
    duration=400
    dt = 0.025
    lems_file_name = 'LEMS_%s.xml'%sim_id
    target_dir = "."

    to_plot = {}
    to_save = {}

    for cell_id in cell_ids:
        cell_file = cell_id+'_active.cell.nml'
        cell_doc = loaders.NeuroMLLoader.load(cell_file)
        print("Loaded morphology file from: "+cell_file)

        cell = cell_doc.cells[0]


        interesting_seg_ids = [0]
        for seg in cell.morphology.segments:
            if '99' in str(seg.id):
                interesting_seg_ids.append(seg.id)

        p_ref = 'Some_voltages_%s'%cell_id
        s_ref = '%s_voltages.dat'%cell_id
        to_plot[p_ref] = []
        to_save[s_ref]=[]

        for seg_id in interesting_seg_ids:
            pop_id = get_pop_id(cell_id)
            to_plot[p_ref].append('%s/0/%s/%s/v'%(pop_id, cell_id,seg_id))
            to_save[s_ref].append('%s/0/%s/%s/v'%(pop_id, cell_id,seg_id))

    generate_lems_file_for_neuroml(sim_id,
                                   nml_file,
                                   target,
                                   duration,
                                   dt,
                                   lems_file_name,
                                   target_dir,
                                   gen_plots_for_all_v = False,
                                   plot_all_segments = False,
                                   gen_plots_for_quantities = to_plot,   #  Dict with displays vs lists of quantity paths
                                   gen_saves_for_all_v = False,
                                   save_all_segments = False,
                                   gen_saves_for_quantities = to_save,   #  Dict with file names vs lists of quantity paths
                                   copy_neuroml = False)



if __name__ == "__main__":

    if '-all' in sys.argv:

        from CreateCellModels import create_active_cell
        cell_ids = []
        for f in os.listdir('..'):
            if f.endswith('.cell.nml') and not '0274' in f and not '0267' in f:
                cell_id = f.split('.')[0]
                print('Loading: %s'%f)
                create_active_cell(cell_id)
                cell_ids.append(cell_id)

        create_network_for_cells(cell_ids, "Net_%iCells"%len(cell_ids))

    elif '-289' in sys.argv:
        cells = {'AA0289'}
        for cell_id in cells:
            create_network_for_cells([cell_id], "Net_%s"%cell_id, stim_amp='600pA')

    else:
        cells = {'AA0173','AA0289'}
        for cell_id in cells:
            create_network_for_cells([cell_id], "Net_%s"%cell_id)
