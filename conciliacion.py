import pandas as pd

def conciliacion_excel(file, tolerancia_dias=3):
    # Leer las dos hojas
    banco = pd.read_excel(file, sheet_name="extracto")
    contab = pd.read_excel(file, sheet_name="contabilidad")

    # Normalizar columnas
    banco["fecha"] = pd.to_datetime(banco["fecha"], dayfirst=True, errors="coerce")
    contab["fecha"] = pd.to_datetime(contab["fecha"], dayfirst=True, errors="coerce")
    banco["importe"] = banco["importe"].round(2)
    contab["importe"] = contab["importe"].round(2)

    banco["_idx"] = banco.index
    contab["_idx"] = contab.index

    usados_b, usados_c = set(), set()
    matches = []

    for bi, brow in banco.iterrows():
        if bi in usados_b:
            continue
        candidatos = contab[(contab["importe"] == brow["importe"]) & (~contab["_idx"].isin(usados_c))]
        if candidatos.empty:
            continue
        cand_ok = candidatos[
            (candidatos["fecha"] >= brow["fecha"] - pd.Timedelta(days=tolerancia_dias)) &
            (candidatos["fecha"] <= brow["fecha"] + pd.Timedelta(days=tolerancia_dias))
        ]
        if cand_ok.empty:
            continue
        mejor = cand_ok.iloc[0]
        usados_b.add(bi)
        usados_c.add(mejor["_idx"])
        matches.append({
            "banco_fecha": brow["fecha"],
            "contab_fecha": mejor["fecha"],
            "importe": brow["importe"],
            "dif_dias": abs((brow["fecha"] - mejor["fecha"]).days)
        })

    conciliados = pd.DataFrame(matches)
    banco_no = banco[~banco["_idx"].isin(usados_b)].drop(columns="_idx")
    contab_no = contab[~contab["_idx"].isin(usados_c)].drop(columns="_idx")

    # Guardar en memoria (BytesIO) en vez de archivo físico
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        conciliados.to_excel(writer, index=False, sheet_name="Conciliados")
        banco_no.to_excel(writer, index=False, sheet_name="Extracto_no_conciliado")
        contab_no.to_excel(writer, index=False, sheet_name="Contab_no_conciliado")
        resumen = pd.DataFrame([{
            "filas_extracto": len(banco),
            "filas_contab": len(contab),
            "coincidencias": len(conciliados),
            "importe_total_extracto": banco["importe"].sum(),
            "importe_total_contab": contab["importe"].sum(),
            "importe_conciliado": conciliados["importe"].sum()
        }])
        resumen.to_excel(writer, index=False, sheet_name="Resumen")

    output.seek(0)
    return output

