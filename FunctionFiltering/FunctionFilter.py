import json
from collections import defaultdict
import numpy as np
def Read_Feature(Feature_Path):
    with open(Feature_Path, 'r') as f:
        ReadJsonContent = json.loads(f.read())
        f.close()

    print(Feature_Path)
    Externals = {}
    for func in ReadJsonContent["imports"]:
        Externals[func[0].replace("L", "", 1)] = func[1]

    nodes = ReadJsonContent["call_graph"]["nodes"]

    # String
    Strings = defaultdict(list)
    for func, funcString in ReadJsonContent["strings"].items():

        if funcString:
            for string in funcString.values():
                string1 = string.strip().replace(" ", "").lower()
                Strings[nodes[func.replace("L", "")]].append(string1)

    edges = ReadJsonContent["call_graph"]["edges"]

    # Imports
    Imports = {}
    Call = defaultdict(dict)
    Called = defaultdict(dict)


    for addr, name in nodes.items():
        if name in Externals.values():
            Imports[addr] = name
        if name.startswith("."):
            Imports[addr] = name.replace(".", "")




    Call_Imports = defaultdict(dict)
    for edge in edges:
        if edge[1] in Externals:
            continue
        if edge[0] in Imports:
            continue
        if edge[1] in Imports:

            if nodes[edge[1]] not in Call_Imports[nodes[edge[0]]]:
                Call_Imports[nodes[edge[0]]][Imports[edge[1]]] = 1
            else:
                Call_Imports[nodes[edge[0]]][Imports[edge[1]]] += 1
        else:

            if nodes[edge[1]] not in Call[nodes[edge[0]]]:
                Call[nodes[edge[0]]][nodes[edge[1]]] = 1
            else:
                Call[nodes[edge[0]]][nodes[edge[1]]] += 1

            if nodes[edge[0]] not in Called[nodes[edge[1]]]:
                Called[nodes[edge[1]]][nodes[edge[0]]] = 1
            else:
                Called[nodes[edge[1]]][nodes[edge[0]]] += 1

    # print(Call_Imports)
    Features = [Strings, Call, Called, Call_Imports, nodes]
    return Features
def Filter(func1, Features1, Functions2, Features2):
    Strings1 = Features1[0]
    Call1 = Features1[1]
    Called1 = Features1[2]
    Imports1 = Features1[3]

    Strings2 = Features2[0]
    Call2 = Features2[1]
    Called2 = Features2[2]
    Imports2 = Features2[3]



    String_Candi_func2s = []

    if func1[2] in Strings1:
        # return []
        Sim = {}
        strings_1 = set(Strings1[func1[2]])
        for func2 in Functions2:
            if func2[2] not in Strings2:
                continue
            strings_2 = set(Strings2[func2[2]])
            inter_strings = strings_1.intersection(strings_2)

            if inter_strings:
                Sim[func2] = (len(inter_strings) * 2) / (len(strings_1) + len(strings_2))

        Rank_Sim = dict(sorted(Sim.items(), key=lambda x: x[1], reverse=True))

        Sims = []
        for func2, sim in Rank_Sim.items():
            if len(Sims) < 1:
                String_Candi_func2s.append(func2)
                if sim not in Sims:
                    Sims.append(sim)
            elif sim in Sims:
                String_Candi_func2s.append(func2)

        if not String_Candi_func2s:
            for func2 in Functions2:
                if func2[2] not in Strings2:
                    continue
                String_Candi_func2s.append(func2)

    if String_Candi_func2s:
        return String_Candi_func2s


    Import_Candi_func2s = []
    if func1[2] in Imports1:
        Sim = {}
        imports_set1 = set(Imports1[func1[2]].keys())
        imports_dict1 = Imports1[func1[2]]
        for func2 in Functions2:
            if func2[2] not in Imports2:
                continue
            imports_set2 = set(Imports2[func2[2]].keys())
            imports_dict2 = Imports2[func2[2]]
            inter_imports = list(imports_set1.intersection(imports_set2))
            if not inter_imports:
                continue

            union_imports = list(imports_set1.union(imports_set2))

            vec1 = []
            for i in union_imports:
                if i in imports_dict1:
                    vec1.append(imports_dict1[i])
                else:
                    vec1.append(0)

            vec2 = []
            for i in union_imports:
                if i in imports_dict2:
                    vec2.append(imports_dict2[i])
                else:
                    vec2.append(0)
            #
            # a_norm = np.linalg.norm(vec1)
            # b_norm = np.linalg.norm(vec2)
            # cos_sim = np.dot(vec1, vec2) / (a_norm * b_norm)

            vector1 = np.array(vec1)
            vector2 = np.array(vec2)
            distance = np.linalg.norm(vector2 - vector1)
            sim = 1/(1+distance)

            Sim[func2] = sim

        Rank_Sim = dict(sorted(Sim.items(), key=lambda x: x[1], reverse=True))

        Sims = []
        for func2, sim in Rank_Sim.items():
            if len(Sims) < 1:
                Import_Candi_func2s.append(func2)
                if sim not in Sims:
                    Sims.append(sim)
            elif sim in Sims:

                Import_Candi_func2s.append(func2)

    if Import_Candi_func2s:
        return Import_Candi_func2s

    if func1[2] not in Called1 and func1[2] not in Call1:
        Call_Candi_func2s = []
        for func2 in Functions2:
            if func2[2] not in Called2 and func2[2] not in Call2:
                Call_Candi_func2s.append(func2)
        return Call_Candi_func2s

    Call_Sim = {}

    if (func1[2] not in Call1) and (func1[2] not in Called1):
        Call_Candi_func2s = []

        for func2 in Functions2:
            if (func2[2] not in Call2) and (func2[2] not in Called2):
                Call_Candi_func2s.append(func2)

        return Call_Candi_func2s

    if func1[2] in Call1:
        call_set1 = set(Call1[func1[2]].keys())
        # print(Call1[func1[2]])
        call_dict1 = Call1[func1[2]]
        rank_call_dict1 = dict(sorted(call_dict1.items(), key=lambda x: x[1], reverse=True))
        call_num1 = list(rank_call_dict1.values())
        for func2 in Functions2:
            if func2[2] in Strings1 or func2[2] in Imports1:
                continue
            if func2[2] in Call2:
                # Call_Sim[func2] = 0
                call_set2 = set(Call2[func2[2]].keys())
                max_call = max(len(call_set1), len(call_set2))
                min_call = max(len(call_set1), len(call_set2))
                if max_call - min_call > 1:
                    continue

                call_dict2 = Call2[func2[2]]
                rank_call_dict2 = dict(sorted(call_dict2.items(), key=lambda x: x[1], reverse=True))
                call_num2 = list(rank_call_dict2.values())
                vec1 = []

                rank_call_list1 = list(rank_call_dict1.values())
                for i in range(max(len(call_num1), len(call_num2))):
                    if i < len(rank_call_list1):
                        vec1.append(rank_call_list1[i])
                    else:
                        vec1.append(0)
                vec2 = []
                rank_call_list2 = list(rank_call_dict2.values())
                for i in range(max(len(call_num1), len(call_num2))):
                    if i < len(rank_call_list2):
                        vec2.append(rank_call_list2[i])
                    else:
                        vec2.append(0)

                vector1 = np.array(vec1)
                vector2 = np.array(vec2)
                distance = np.linalg.norm(vector2 - vector1)
                sim = 1/(1+distance)

                Call_Sim[func2] = sim

                # for i in range(min(len(call_num1),len(call_num2))):
                #     Call_Sim[func2] += min(call_num1[i], call_num2[i])

    Called_Sim = {}

    if func1[2] in Called1:
        # print(func1)
        called_set1 = set(Called1[func1[2]].keys())
        # print(Called1[func1[2]])
        called_dict1 = Called1[func1[2]]
        rank_called_dict1 = dict(sorted(called_dict1.items(), key=lambda x: x[1], reverse=True))
        called_num1 = list(rank_called_dict1.values())

        for func2 in Functions2:
            if func2[2] in Strings1 or func2[2] in Imports1:
                continue
            if func2[2] in Called2:
                # Called_Sim[func2] = 0
                called_set2 = set(Called2[func2[2]].keys())
                max_called = max(len(called_set1), len(called_set2))
                min_called = min(len(called_set1), len(called_set2))
                if max_called - min_called > 1:
                    continue
                called_dict2 = Called2[func2[2]]
                rank_called_dict2 = dict(sorted(called_dict2.items(), key=lambda x: x[1], reverse=True))
                called_num2 = list(rank_called_dict2.values())

                vec1 = []

                rank_called_list1 = list(rank_called_dict1.values())
                for i in range(max(len(called_num1), len(called_num2))):
                    if i < len(rank_called_list1):
                        vec1.append(rank_called_list1[i])
                    else:
                        vec1.append(0)
                vec2 = []
                rank_called_list2 = list(rank_called_dict2.values())
                for i in range(max(len(called_num1), len(called_num2))):
                    if i < len(rank_called_list2):
                        vec2.append(rank_called_list2[i])
                    else:
                        vec2.append(0)

                vector1 = np.array(vec1)
                vector2 = np.array(vec2)
                distance = np.linalg.norm(vector2 - vector1)
                sim = 1/(1+distance)

                Called_Sim[func2] = sim

    Call_Candi_func2s = []
    Rank_Sim = {}
    if Call_Sim and Called_Sim:
        inter = list(set(Call_Sim.keys()).intersection(set(Called_Sim.keys())))
        if inter:
            Sim = {}

            for func2 in inter:
                Sim[func2] = Call_Sim[func2] + Called_Sim[func2]
            Rank_Sim = dict(sorted(Sim.items(), key=lambda x: x[1], reverse=True))
        else:
            Sim = {}
            for func2 in Call_Sim:
                Sim[func2] = Call_Sim[func2]
            for func2 in Called_Sim:
                Sim[func2] = Called_Sim[func2]
            Rank_Sim = dict(sorted(Sim.items(), key=lambda x: x[1], reverse=True))

    elif Call_Sim:
        Rank_Sim = dict(sorted(Call_Sim.items(), key=lambda x: x[1], reverse=True))
    elif Called_Sim:
        Rank_Sim = dict(sorted(Called_Sim.items(), key=lambda x: x[1], reverse=True))

    Sims = []
    for func2, sim in Rank_Sim.items():
        if len(Sims) < 1:
            Call_Candi_func2s.append(func2)
            if sim not in Sims:
                Sims.append(sim)
        elif sim in Sims:
            Call_Candi_func2s.append(func2)

    return Call_Candi_func2s