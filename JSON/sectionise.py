#!/usr/bin/env python3
"""
Enter one line description here.

File:

Copyright 2022 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import neuroml
from neuroml.loaders import read_neuroml2_file
import neuroml.writers as writers


def sectionise(cell: neuroml.Cell, root_segment_id: int, use_convention=True):
    """Create sections of branches for the provided cell.

    This function will create new unbranched, contiguous segment groups that
    consist of sections between two branch points.

    Note that the first segment (root segment) of a branch must have a proximal
    point that connects it to the rest of the neuronal morphology. If, when
    constructing these branches, a root segment is found that does not include
    a proximal point, one will be added using the `get_actual_proximal` method.

    No other changes will be made to any segments, or to any pre-existing
    segment groups.

    :param cell: cell to sectionise
    :type cell: neuroml.Cell
    :param root_segment_id: id of segment considered the root of the tree,
        generally the first soma segment
    :type root_segment_id: int
    :param use_convention: toggle using NeuroML convention for segment groups
    :type use_convention: bool
    :returns: modified cell with new section groups
    :rtype: neuroml.Cell

    """
    # get morphology tree
    morph_tree = get_segment_adjacency_list(cell)

    # initialise root segment and first segment group
    seg = cell.get_segment(root_segment_id)
    group_name = f"seg_group_{len(cell.morphology.segment_groups) - 1}_seg_{seg.id}"
    new_seg_group = cell.add_unbranched_segment_group(group_name)

    # run recursive function
    __sectionise(cell, root_segment_id, new_seg_group, morph_tree)


def __sectionise(cell: neuroml.Cell, root_segment_id: int, seg_group:
                 neuroml.SegmentGroup, morph_tree: dict[int, list[int]]):
    """Main recursive sectionising method.

    :param cell: cell to sectionise
    :type cell: neuroml.Cell
    :param root_segment_id: id of root of branch
    :type root_segment_id: int
    :returns: TODO

    """
    # print(f"Processing element: {root_segment_id}")

    try:
        children = morph_tree[root_segment_id]
        # keep going while there's only one child
        # no need to use recursion here---hits Python's recursion limits in
        # long segment groups
        # - if there are no children, it'll go to the except block
        # - if there are more than one children, it'll go to the next
        # conditional
        while len(children) == 1:
            seg_group.add("Member", segments=root_segment_id)
            root_segment_id = children[0]
            children = morph_tree[root_segment_id]
        # if there are more than one children, we've reached the end of this
        # segment group but not of the branch. New segment groups need to start
        # from here.
        if len(children) > 1:
            # this becomes the last segment of the current segment group
            seg_group.add("Member", segments=root_segment_id)

            # each child will start a new segment group
            for child in children:
                seg = cell.get_segment(child)
                # Ensure that a proximal point is set.
                # This is required for the first segment of unbranched segment
                # groups
                seg.proximal = cell.get_actual_proximal(seg.id)
                group_name = f"seg_group_{len(cell.morphology.segment_groups) - 1}_seg_{seg.id}"
                new_seg_group = cell.add_unbranched_segment_group(group_name)

                __sectionise(cell, child, new_seg_group, morph_tree)
    # if there are no children, it's a leaf node, so we just add to the current
    # seg_group and do nothing else
    except KeyError:
        seg_group.add("Member", segments=root_segment_id)


def get_segment_adjacency_list(cell: neuroml.Cell) -> dict[int, list[int]]:
    """Get the adjacency list of all segments in the cell morphology.
    Returns a dict where each key is a parent segment, and the value is the
    list of its children segments.

    Segment without children (leaf segments) are not included as parents in the
    adjacency list.

    :param cell: cell to get adjacency list for
    :type cell: neuroml.Cell
    :returns: dict with parent segments as keys and their children as values
    :rtype: dict

    """
    # create data structure holding list of children for each segment
    child_lists = {}  # type: dict[int, list[int]]
    for segment in cell.morphology.segments:
        try:
            parent = segment.parent.segments
            if parent not in child_lists:
                child_lists[parent] = []
            child_lists[parent].append(segment.id)
        except AttributeError:
            print(f"Warning: Segment: {segment} has no parent")

    return child_lists


if __name__ == "__main__":
    cell_doc = read_neuroml2_file("../NeuroML2/AA0274.cell.nml")
    cell = cell_doc.cells[0]
    # print(cell.summary())
    sectionise(cell, root_segment_id=0)
    # print(cell.summary())
    writers.NeuroMLWriter.write(cell_doc, "../NeuroML2/AA0274-new.cell.nml")
    # cell.morphology.info(show_contents=True)
