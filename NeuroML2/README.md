## MouseLight Showcase cells in NeuroML2 format

A number of the cellular reconstructions from the [Janelia MouseLight project](https://www.janelia.org/project-team/mouselight)
 have been converted to [NeuroML](http://www.neuroml.org) format and can be visualised on OSB. 

The original data were made available by the [Janelia MouseLight project](https://www.janelia.org/project-team/mouselight) 
under the CC-BY NC license, https://creativecommons.org/licenses/by-nc/4.0/legalcode. 

The script to perform the transformation of the downloaded JSON files is 
[export.py](https://github.com/OpenSourceBrain/MouseLightShowcase/blob/master/JSON/export.py) and uses [libNeuroML](https://github.com/NeuralEnsemble/libNeuroML).

To use this script:
```
pip install libNeuroML
git clone https://github.com/OpenSourceBrain/MouseLightShowcase.git
cd MouseLightShowcase/JSON
python export.py
```

**NOTE: cells have been given a spherical soma for visualisation purposes. However, 
no soma has been reconstructed from the original cells.**

The cells which have been converted so far include:
- AA0052: https://doi.org/10.25378/janelia.5521753 ([NeuroML file](../NeuroML2/AA0052.cell.nml))
- AA0289: https://doi.org/10.25378/janelia.5527822 ([NeuroML file](../NeuroML2/AA0289.cell.nml))
- AA0274: https://doi.org/10.25378/janelia.5527774 ([NeuroML file](../NeuroML2/AA0274.cell.nml))
- AA0267: https://doi.org/10.25378/janelia.5527747 ([NeuroML file](../NeuroML2/AA0267.cell.nml))
- AA0261: https://doi.org/10.25378/janelia.5527717 ([NeuroML file](../NeuroML2/AA0261.cell.nml))
- AA0250: https://doi.org/10.25378/janelia.5527678 ([NeuroML file](../NeuroML2/AA0250.cell.nml))
- AA0188: https://doi.org/10.25378/janelia.5527468 ([NeuroML file](../NeuroML2/AA0188.cell.nml))
- AA0182: https://doi.org/10.25378/janelia.5527447 ([NeuroML file](../NeuroML2/AA0182.cell.nml))
- AA0180: https://doi.org/10.25378/janelia.5527441 ([NeuroML file](../NeuroML2/AA0180.cell.nml))
- AA0257: https://doi.org/10.25378/janelia.5527702 ([NeuroML file](../NeuroML2/AA0257.cell.nml))
- AA0252: https://doi.org/10.25378/janelia.5527684 ([NeuroML file](../NeuroML2/AA0252.cell.nml))
- AA0248: https://doi.org/10.25378/janelia.5527672 ([NeuroML file](../NeuroML2/AA0248.cell.nml))
- AA0173: https://doi.org/10.25378/janelia.5527420 ([NeuroML file](../NeuroML2/AA0173.cell.nml))
- AA0171: https://doi.org/10.25378/janelia.5527414 ([NeuroML file](../NeuroML2/AA0171.cell.nml))
- AA0158: https://doi.org/10.25378/janelia.5527369 ([NeuroML file](../NeuroML2/AA0158.cell.nml))
- AA0157: https://doi.org/10.25378/janelia.5527366 ([NeuroML file](../NeuroML2/AA0157.cell.nml))

- AA0271: https://doi.org/10.25378/janelia.5527762 ([NeuroML file](../NeuroML2/AA0271.cell.nml))
- AA0184: https://doi.org/10.25378/janelia.5527453 ([NeuroML file](../NeuroML2/AA0184.cell.nml))
- AA0131: https://doi.org/10.25378/janelia.5527267 ([NeuroML file](../NeuroML2/AA0131.cell.nml))