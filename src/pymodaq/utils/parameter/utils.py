from __future__ import annotations

from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from pymodaq.utils.parameter import Parameter


def get_widget_from_tree(parameter_tree, widget_instance):
    widgets = []
    for item in parameter_tree.listAllItems():
        if hasattr(item, 'widget'):
            if item.widget.__class__.__name__ == widget_instance.__name__:
                widgets.append(item.widget)
    return widgets


def get_param_path(param):
    """

    Parameters
    ----------
    param

    Returns
    -------

    """
    path = [param.name()]
    while param.parent() is not None:
        path.append(param.parent().name())
        param = param.parent()
    return path[::-1]


def iter_children(param, childlist=[]):
    """Get a list of parameters name under a given Parameter
        | Returns all childrens names.

        =============== ================================= ====================================
        **Parameters**   **Type**                           **Description**
        *param*          instance of pyqtgraph parameter    the root node to be coursed
        *childlist*      list                               the child list recetion structure
        =============== ================================= ====================================

        Returns
        -------
        childlist : parameter list
            The list of the children from the given node.
    """
    for child in param.children():
        childlist.append(child.name())
        if 'group' in child.type():
            childlist.extend(iter_children(child, []))
    return childlist


def iter_children_params(param, childlist=[]):
    """Get a list of parameters under a given Parameter

    """
    for child in param.children():
        childlist.append(child)
        if 'group' in child.type():
            childlist.extend(iter_children_params(child, []))
    return childlist


def get_param_from_name(parent, name) -> Parameter:
    """Get Parameter under parent whose name is name

    Parameters
    ----------
    parent: Parameter
    name: str

    Returns
    -------
    Parameter
    """
    for child in parent.children():
        if child.name() == name:
            return child
        if 'group' in child.type():
            ch = get_param_from_name(child, name)
            if ch is not None:
                return ch


def is_name_in_dict(dict_tmp, name):
    if 'name' in dict_tmp:
        if dict_tmp['name'] == name:
            return True
    return False


def get_param_dict_from_name(parent_list, name, pop=False):
    """Get dict under parent whose name is name. The parent_list structure is the one used to init a Parameter object

    Parameters
    ----------
    parent_list: (list of dicts) as defined to init Parameter object
    name: (str) value to find for the key: name
    pop: (bool) if True remove the matched dict from parent

    Returns
    -------
    dict the matched dict
    """
    for index, parent_dict in enumerate(parent_list):
        if is_name_in_dict(parent_dict, name):
            if pop:
                return parent_list.pop(index)
            else:
                return parent_dict

        elif 'children' in parent_dict:
            ch = get_param_dict_from_name(parent_dict['children'], name, pop)
            if ch is not None:
                return ch


if __name__ == '__main__':              # pragma: no cover
    parent = [
        {'title': 'Spectro Settings:', 'name': 'spectro_settings', 'type': 'group', 'expanded': True,
            'children': [
                {'title': 'Home Wavelength (nm):', 'name': 'spectro_wl_home', 'type': 'float', 'value': 600, 'min': 0,
                 'readonly': False},
                {'title': 'Grating Settings:', 'name': 'grating_settings', 'type': 'group', 'expanded': True,
                    'children': [
                        {'title': 'Grating:', 'name': 'grating', 'type': 'list'},
                        {'title': 'Lines (/mm):', 'name': 'lines', 'type': 'int', 'readonly': True},
                        {'title': 'Blaze WL (nm):', 'name': 'blaze', 'type': 'str', 'readonly': True},
                    ]},
            ]
         },
    ]

    d = get_param_dict_from_name(parent, 'lines')

    d['readonly'] = False
    print(parent[0]['children'][1]['children'])


def set_param_from_param(param_old, param_new):
    """
        Walk through parameters children and set values using new parameter values.
    """
    for child_old in param_old.children():
        # try:
        path = param_old.childPath(child_old)
        child_new = param_new.child(*path)
        param_type = child_old.type()

        if 'group' not in param_type:  # covers 'group', custom 'groupmove'...
            # try:
            if 'list' in param_type:  # check if the value is in the limits of the old params
                # (limits are usually set at initialization) but carefull as such paramater limits can be a list or a
                # dict object
                if isinstance(child_old.opts['limits'], list):
                    if child_new.value() not in child_old.opts['limits']:
                        child_old.opts['limits'].append(child_new.value())
                elif isinstance(child_old.opts['limits'], dict):
                    if child_new.value() not in child_old.opts['limits'].values():
                        child_old.opts['limits'].update(dict(str(child_new.value()), child_new.value()))

                child_old.setValue(child_new.value())
            elif 'str' in param_type or 'browsepath' in param_type or 'text' in param_type:
                if child_new.value() != "":  # to make sure one doesnt overwrite something
                    child_old.setValue(child_new.value())
            else:
                child_old.setValue(child_new.value())
            # except Exception as e:
            #    print(str(e))
        else:
            set_param_from_param(child_old, child_new)
        # except Exception as e:
        #    print(str(e))


def scroll_log(scroll_val, min_val, max_val):
    """
    Convert a scroll value [0-100] to a log scale between min_val and max_val
    Parameters
    ----------
    scroll
    min_val
    max_val
    Returns
    -------

    """
    assert scroll_val >= 0
    assert scroll_val <= 100
    value = scroll_val * (np.log10(max_val) - np.log10(min_val)) / 100 + np.log10(min_val)
    return 10 ** value


def scroll_linear(scroll_val, min_val, max_val):
    """
    Convert a scroll value [0-100] to a linear scale between min_val and max_val
    Parameters
    ----------
    scroll
    min_val
    max_val
    Returns
    -------

    """
    assert scroll_val >= 0
    assert scroll_val <= 100
    value = scroll_val * (max_val - min_val) / 100 + min_val
    return value
