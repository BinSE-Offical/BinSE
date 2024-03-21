#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------File Info-----------------------
Name: fg_cg_ie_table_ida.py
Description: generate callee relations and import export table
Author: GentleCP
Email: me@gentlecp.com
Create Date: 2022/8/31
-----------------End-----------------------------
"""
import idaapi
import idautils
import idc

import pickle as pkl
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
import networkx as nx
import json



class CallViewer(object):
    """
    generate caller and callee for each function
    """

    def __init__(self):
        # self._callee_graph = nx.DiGraph()
        self._nodes = {}
        self._edges = []

    def get_callee_graph(self):
        """
        :return: callee_graph
        """
        if self._nodes and self._edges:
            return self._nodes, self._edges


        for callee_ea in idautils.Functions():
            callee_name = idaapi.get_func_name(callee_ea)

            if hex(callee_ea).strip("L") not in self._nodes:
                self._nodes[hex(callee_ea).strip("L")] = callee_name

            for caller_ea in idautils.CodeRefsTo(callee_ea, 0):
                caller_func = idaapi.get_func(caller_ea)
                caller_name = idaapi.get_func_name(caller_ea)

                if caller_func:
                    if hex(caller_func.startEA).strip("L") not in self._nodes:
                        self._nodes[hex(caller_func.startEA).strip("L")] = caller_name

                    self._edges.append([hex(caller_func.startEA).strip("L"), hex(callee_ea).strip("L")])


        return self._nodes, self._edges




class IEViewer(object):
    """
    generate import and export table list
    """

    def __init__(self):
        self._imports = []
        self._exports = []

    def imports_names_cb(self, ea, name, ord):
        tmp = name.split('@@')
        if len(tmp) == 1:
            self._imports.append([ord, hex(ea), tmp[0], ''])
        else:
            self._imports.append([ord, hex(ea), tmp[0], tmp[1]])
        return True

    def get_imports(self, only_name=False):
        if self._imports:
            # return [item[2:] for item in self._imports] if only_name else self._imports
            return [item[1:] for item in self._imports] if only_name else self._imports

        nimps = idaapi.get_import_module_qty()
        for i in range(nimps):
            idaapi.enum_import_names(i, self.imports_names_cb)
        self._imports.sort(key=lambda x: x[2])
        # return [item[2:] for item in self._imports] if only_name else self._imports
        return [item[1:] for item in self._imports] if only_name else self._imports

    def get_exports(self, only_name=False):
        if self._exports:
            # return [item[3] for item in self._exports] if only_name else self._exports
            return [[hex(item[1]), hex(item[2]), item[3]] for item in self._exports] if only_name else self._exports
        self._exports = list(idautils.Entries())
        # return [item[3] for item in self._exports] if only_name else self._exports
        return [[hex(item[1]), hex(item[2]), item[3]] for item in self._exports] if only_name else self._exports

    def save(self, save_path='imports_exports.json', only_name=False):
        save_data = {
            'imports': self.get_imports(only_name),
            'exports': self.get_exports(only_name),
        }

        file_path = Path(save_path)
        with file_path.open('wt') as handle:
            json.dump(save_data, handle, indent=4, sort_keys=True)

        # write_json(save_data, save_path)

class StrViewer(object):
    def __init__(self):
        self._strings = {}



    def get_strings(self, ):
        if self._strings:
            return self._strings

        Strings = list(idautils.Strings())

        for f_addr in idautils.Functions():


            func = idaapi.get_func(f_addr)
            if func is None:
               continue


            f_strings = {}
            for bb in idaapi.FlowChart(func):
                if bb.end_ea - bb.start_ea > 0:
                    d_from = []

                    for h in idautils.Heads(bb.start_ea, bb.end_ea):
                        for xf in idautils.DataRefsFrom(h):
                            d_from.append(xf)
                    for k in Strings:
                        if k.ea in d_from:
                            f_strings[hex(k.ea)] = str(k)

            if f_strings:
                # f_name = idc.get_func_name(f_addr)
                self._strings[hex(f_addr)] = f_strings

                # self._strings[(hex(f_addr), f_name)] = f_strings

        return self._strings









def main():
    nodes, edges = CallViewer().get_callee_graph()
    ie_viewer = IEViewer()
    str_viewer = StrViewer()
    if len(idc.ARGV) == 2:
        save_path = idc.ARGV[1]
    else:
        bin_path = Path(idc.get_input_file_path()).resolve()
        # save_path = bin_path.parent.joinpath(f'cg_ie_table.pkl')
        save_path = "%s_%s"%(bin_path, 'cg_ie_str.json')


    import_funcs = ie_viewer.get_imports(only_name=True)
    export_funcs = ie_viewer.get_exports(only_name=True)
    strings = str_viewer.get_strings()

    cg = {
        "nodes":nodes,
          "edges":edges
    }

    writecontent = {
        'call_graph': cg,
        'imports': import_funcs,
        'exports': export_funcs,
        'strings': strings
    }

    with open(save_path, "w") as f_out:
        json.dump(writecontent, f_out)



if __name__ == '__main__':
    idaapi.auto_wait()
    main()
    idc.qexit(0)
