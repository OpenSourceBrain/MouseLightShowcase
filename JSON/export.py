'''

This file will convert JSON files downloaded from the Janelia MouseLight project 
(https://www.janelia.org/project-team/mouselight) in JSON format to NeuroML2

'''

import neuroml
import sys
import json
import neuroml.writers as writers

nml2_readme = '../NeuroML2/README.md'

def export_to_nml2(filename, ref, soma_diameter):
    
    rm = open(nml2_readme)
    readme_text = rm.read()
    rm.close()
    
    with open(filename, "r") as json_file:
        json_info = json.load(json_file)
        
    print("Opened %s with info: %s"%(filename, json_info.keys()))
    
    net_doc = neuroml.NeuroMLDocument(id='Net_%s'%ref)
    

    net = neuroml.Network(id=net_doc.id)
    net_doc.networks.append(net)
    
    for n in json_info['neurons']:
        
        id = str(n['idString'])
        print("============================\nLooking at neuron: %s"%(id))
        cell_doc = neuroml.NeuroMLDocument(id=id)
        cell = neuroml.Cell(id=id)
        
        notes = '''\n    Cell %s downloaded from Janelia MouseLight project (https://www.janelia.org/project-team/mouselight)\n    and converted to NeuroML'''%id
        notes += '\n    DOI of original cell: https://doi.org/%s'%n['DOI']
        notes += '\n\n    NOTE: cells have been given a soma of diameter %sum for visualisation purposes'%soma_diameter
        notes += '\n    However, no soma has been reconstructed from the original cells'
        
        cell.notes = notes
        
        if not n['DOI'] in readme_text:
            readme_text+='\nhttps://doi.org/%s ([NeuroML file](../NeuroML2/%s.cell.nml))'%(n['DOI'],id)
        
        for k in ['idString','DOI','sample/date','sample/strain','label/virus','label/fluorophore']:
            
            if '/' in k:
                k1=k.split('/')[0]
                k2=k.split('/')[1]       
                p = neuroml.Property(tag='JaneliaMouseLight:%s_%s'%(k1,k2), value=n[k1][k2])
                cell.properties.append(p)
            else:
                p = neuroml.Property(tag='JaneliaMouseLight:%s'%k, value=n[k])
                cell.properties.append(p)

        net_doc.includes.append(neuroml.IncludeType(cell.id+'.cell.nml')) 

        pop = neuroml.Population(id="pop_"+cell.id,
                    component=cell.id,
                    type="populationList")

        inst = neuroml.Instance(id="0")
        pop.instances.append(inst)
        inst.location = neuroml.Location(x=0, y=0, z=0)
        net.populations.append(pop)
        
        cell_doc.cells.append(cell)
        cell.morphology = neuroml.Morphology(id='morph_%s'%id)
        
        id_vs_seg = {}
        soma_id = 0
        soma = neuroml.Segment(id=soma_id, name='soma')
        cell.morphology.segments.append(soma)
        soma.proximal = neuroml.Point3DWithDiam(x=float(n['soma']['x']) ,y=float(n['soma']['y']),z=float(n['soma']['z']),diameter=soma_diameter)
        soma.distal = neuroml.Point3DWithDiam(x=float(n['soma']['x']) ,y=float(n['soma']['y']),z=float(n['soma']['z']),diameter=soma_diameter)
        id_vs_seg[0]=soma
        
        last_seg_id = -2
        
        offsets = {'axon':1000,'dendrite':1000000}
        
        for sg in offsets.keys():
        
            for a in n[sg]:
                id = int(a['sampleNumber'])+offsets[sg]
                name = '%s_%i'%(sg,id)
                seg = neuroml.Segment(id=id, name=name)
                seg.distal = neuroml.Point3DWithDiam(x=float(a['x']) ,y=float(a['y']),z=float(a['z']),diameter=float(a['radius'])*2)

                parent = int(a['parentNumber'])

                if parent==-1:
                    seg.parent = neuroml.SegmentParent(segments=soma.id)
                    parent = 0
                else:
                    parent += offsets[sg]
                    seg.parent = neuroml.SegmentParent(segments=parent)

                if parent!=last_seg_id or parent == 0 :
                    seg_parent = id_vs_seg[parent]
                    seg.proximal = neuroml.Point3DWithDiam(x=seg_parent.distal.x,
                                                           y=seg_parent.distal.y,
                                                           z=seg_parent.distal.z,
                                                           diameter=seg_parent.distal.diameter)
                    if parent == 0:
                        seg.proximal.diameter = seg.distal.diameter

                last_seg_id = seg.id
                id_vs_seg[id] = seg
                cell.morphology.segments.append(seg)
            

        axon_seg_group = neuroml.SegmentGroup(id="axon_group",neuro_lex_id="GO:0030424")  # See http://amigo.geneontology.org/amigo/term/GO:0030424
        soma_seg_group = neuroml.SegmentGroup(id="soma_group",neuro_lex_id="GO:0043025")
        dend_seg_group = neuroml.SegmentGroup(id="dendrite_group",neuro_lex_id="GO:0030425")
        
        for seg in cell.morphology.segments:
    
            if 'axon' in seg.name:
                axon_seg_group.members.append(neuroml.Member(segments=seg.id))
            elif 'soma' in seg.name:
                soma_seg_group.members.append(neuroml.Member(segments=seg.id))
            elif 'dend' in seg.name:
                dend_seg_group.members.append(neuroml.Member(segments=seg.id))
            else:
                raise Exception("Segment: %s is not axon, dend or soma!"%seg)


        cell.morphology.segment_groups.append(axon_seg_group)
        cell.morphology.segment_groups.append(soma_seg_group)
        cell.morphology.segment_groups.append(dend_seg_group)


        nml_file = '../NeuroML2/%s.cell.nml'%cell.id

        writers.NeuroMLWriter.write(cell_doc,nml_file)

        print("Saved cell file to: "+nml_file)
        

    nml_file = '../NeuroML2/%s.net.nml'%net.id

    writers.NeuroMLWriter.write(net_doc,nml_file)

    print("Saved network file to: "+nml_file)
    
    print readme_text
    
    rm = open(nml2_readme,'w')
    rm.write(readme_text)
    rm.close()

if __name__ == "__main__":
    
    files = {'MOp':'MOp.json','AA0052':'AA0052.json'}
    #files = {'AA0052':'AA0052.json'}
    
    for f in files:
        export_to_nml2(files[f], f, soma_diameter=20)


