"""
evaluation.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-10-15

Usage: python evaluation.py -qrels <qrelsFileName> -results <resultsFileName> -output <outputFileName>
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm 

def normalize_doc_id(doc_uri):
    return doc_uri.rstrip('/').split('/')[-1]

def prec_at_k(k, results, qrels):
    docs_relev_recup = 0
    i = 0
    for doc_id in results:
        if i >= k:
            break
        
        if qrels.get(doc_id, 0) == 1:
            docs_relev_recup += 1
        i+=1
    return docs_relev_recup / k

def rec_at_k(k, results, qrels):
    docs_relev_recup = 0
    docs_relev = 0
    i = 0
    for doc_id in qrels:
        if qrels.get(doc_id, 0) == 1:
            docs_relev += 1
    
    for doc_id in results:
        if i >= k:
            break

        if qrels.get(doc_id, 0) == 1:
            docs_relev_recup += 1
        i+=1
    
    return docs_relev_recup / docs_relev if docs_relev > 0 else 0

def avg_prec(results, qrels):
    suma = 0
    cont = 0
    for i, doc_id in enumerate(results, start=1):
        if qrels.get(doc_id, 0) == 1:
            cont += 1
            suma += prec_at_k(i, results, qrels)
    return suma/cont

def rec_prec(results, qrels):
    relevant = {d for d, r in qrels.items() if r == 1}
    aux = []
    relevant_rec = 0
    num_relevant = len(relevant)
    for i, doc in enumerate(results, start = 1):
        if doc in relevant:
            relevant_rec += 1
        rec = relevant_rec / num_relevant if num_relevant > 0 else 0
        prec = relevant_rec / i
        if doc in relevant:
            aux.append((rec,prec))
        
    return aux


def print_interpolated_rec_prec(rec_prec):
    aux = []

    for valor in np.arange(0.0, 1.1, 0.1):
        max_prec = 0
        for rec, prec in rec_prec:
            if rec >= valor and prec > max_prec:
                max_prec = prec
        
        aux.append((valor, max_prec))
    
    return aux

def generate_interpol_plot(total_inter_rec_prec, show_all=False):
    """Genera y guarda el gráfico de exhaustividad-precisión interpolada."""
    fig, ax = plt.subplots()

    # Colores distintos para cada necesidad de información
    colors = cm.tab10(np.linspace(0, 1, len(total_inter_rec_prec)))

    # Curvas por necesidad de información (Poner show_all=True para mostrarlas)
    if show_all:
        for i, (inter_rec_prec, color) in enumerate(zip(total_inter_rec_prec, colors)):
            recalls = [rp[0] for rp in inter_rec_prec]
            precisions = [rp[1] for rp in inter_rec_prec]
            ax.plot(
                recalls,
                precisions,
                color=color,
                label=f'information need {i+1}',
                linewidth=1.5
            )

    # Curva promedio (Total)
    recalls_total = np.arange(0.0, 1.1, 0.1)
    precisions_total = [np.mean([interp[i][1] for interp in total_inter_rec_prec]) for i in range(11)]
    ax.plot(
        recalls_total,
        precisions_total,
        color='black',
        label='Total',
        linewidth=2
    )

    # Añadir tus datos manuales, para hacer comparación
    #recalls_manual = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    #precisions_a = [0.946, 0.807, 0.77, 0.67, 0.599, 0.191, 0.0, 0.0, 0.0, 0.0, 0.0]
    #precisions_b = [0.795, 0.569, 0.44, 0.36, 0.195, 0.195, 0.191, 0.0, 0.0, 0.0, 0.0]

    #ax.plot(recalls_manual, precisions_a, linestyle='-', color='red', label='System a')
    #ax.plot(recalls_manual, precisions_b, linestyle='-', color='blue', label='System b')

    # Configuración del gráfico
    ax.set_xlabel('exhaustividad (recall)')
    ax.set_ylabel('precisión')
    ax.set_xlim(0, 1.0)
    ax.set_xticks(np.arange(0.0, 1.1, 0.1))
    ax.set_ylim(0, 1.05)
    ax.set_yticks(np.arange(0.0, 1.3, 0.2))
    ax.legend(loc='upper right')
    ax.yaxis.grid(True, linestyle='-', alpha=0.6)

    # Guardar y mostrar
    plt.tight_layout()
    plt.savefig('precision_recall_curve.png', dpi=300)
    plt.show()

if __name__ == '__main__':
    qrelsfile = None
    resultsfile = None
    outputfile = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-qrels':
            qrelsfile = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-results':
            resultsfile = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-output':
            outputfile = sys.argv[i + 1]
            i = i + 1
        i = i + 1

    if not qrelsfile or not resultsfile or not outputfile:
        print("Usage: python evaluation.py -qrels <qrelsFileName> -results <resultsFileName> -output <outputFileName>")
        sys.exit(1)

    # Leer el archivo de qrels
    qrels = {}

    with open(qrelsfile, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                query_id, doc_id, relevance = parts
                if query_id not in qrels:
                    qrels[query_id] = {}
                norm_id = normalize_doc_id(doc_id)
                qrels[query_id][norm_id] = int(relevance)
    
    # Leer el archivo de resultados
    results = {}

    with open(resultsfile, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                query_id, doc_id = parts
                if query_id not in results:
                    results[query_id] = []
                norm_id = normalize_doc_id(doc_id)
                results[query_id].append(norm_id)

    # Asegurarse de que todas las necesidades de información en results estén en qrels
    for qid in results:
        qrels.setdefault(qid, {})


    with open(outputfile, 'w') as f:
        total_precision = 0
        total_recall = 0
        total_f1 = 0
        total_prec10 = 0
        total_MAP = 0
        total_inter_rec_prec = []

        for info_need in results:
            docs_recup = len(results[info_need])
            docs_relev_recup = 0
            docs_relev = len([d for d, r in qrels[info_need].items() if r == 1])

            qrels_for_need = qrels.get(info_need, {})

            for doc_id in results[info_need]:
                if qrels_for_need.get(doc_id, 0) == 1:
                    docs_relev_recup += 1

            f.write(f"INFORMATION_NEED {info_need}\n")

            precision = docs_relev_recup/docs_recup
            f.write(f"precision {precision:.3f}\n")
            total_precision += precision

            recall = docs_relev_recup/docs_relev if docs_relev > 0 else 0
            f.write(f"recall {recall:.3f}\n")
            total_recall += recall

            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            f.write(f"F1 {f1:.3f}\n")
            total_f1 += f1

            prec10 = docs_relev_recup/10 if (docs_recup < 10) else prec_at_k(10, results[info_need], qrels[info_need])
            f.write(f"prec@10 {prec10:.3f}\n")
            total_prec10 += prec10
            
            av_prec = 0 if (docs_relev_recup == 0) else avg_prec(results[info_need], qrels[info_need])
            f.write(f"average_precision {av_prec:.3f}\n")
            total_MAP += av_prec

            rec_pre = rec_prec(results[info_need], qrels[info_need])
            f.write(f"recall_precision\n")
            for recall_point, prec_point in rec_pre:
                f.write(f"{recall_point:.3f}\t{prec_point:.3f}\n")
            
            inter_rec_prec = print_interpolated_rec_prec(rec_pre)
            f.write("interpolated_recall_precision\n")
            for recall_point, prec_point in inter_rec_prec:
                f.write(f"{recall_point:.3f}\t{prec_point:.3f}\n")
            total_inter_rec_prec.append(inter_rec_prec)
            
            f.write("\n")
        
        # Media de las métricas
        f.write("TOTAL\n")
        total_info_needs = len(results)

        total_precision = total_precision / total_info_needs
        f.write(f"precision {total_precision:.3f}\n")

        total_recall = total_recall / total_info_needs
        f.write(f"recall {total_recall:.3f}\n")

        total_f1 = total_f1 / total_info_needs
        f.write(f"F1 {total_f1:.3f}\n")

        total_prec10 = total_prec10 / total_info_needs
        f.write(f"prec@10 {total_prec10:.3f}\n")

        total_MAP = total_MAP / total_info_needs
        f.write(f"MAP {total_MAP:.3f}\n")

        f.write("interpolated_recall_precision\n")
        for i, valor in enumerate(np.arange(0.0, 1.1, 0.1)):
            prom = np.mean([interp[i][1] for interp in total_inter_rec_prec])
            f.write(f"{valor:.3f}\t{prom:.3f}\n")

    generate_interpol_plot(total_inter_rec_prec)  # Descomenta para generar el gráfico