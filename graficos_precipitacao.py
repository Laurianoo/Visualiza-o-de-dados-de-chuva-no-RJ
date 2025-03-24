import os
import pandas as pd
import matplotlib.pyplot as plt

# Função para carregar os dados das estações
def carregar_dados(workspace, estacoes_file):
    files = [file for file in os.listdir(workspace) if file.endswith("_Chuvas.csv")]
    acumulados = {}

    for file in files:
        caminho_csv = os.path.join(workspace, file)
        try:
            df = pd.read_csv(caminho_csv, encoding='iso-8859-1', sep=';', skiprows=14, on_bad_lines='skip')
            if 'Data' not in df.columns:
                raise KeyError("Coluna 'Data' não encontrada no arquivo.")

            precip_columns = [col for col in df.columns if col.startswith('Chuva') and not col.endswith('Status')]
            cols_to_keep = ['Data'] + precip_columns
            df = df[cols_to_keep]
            df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            df[precip_columns] = df[precip_columns].replace(',', '.', regex=True).apply(pd.to_numeric, errors='coerce')
            df = df[(df['Data'] >= '2000-01-01') & (df['Data'] <= '2024-12-31')]
            df['MesAno'] = df['Data'].dt.to_period('M')
            df_acumulado = df.groupby('MesAno')[precip_columns].sum().reset_index()
            acumulados[file] = df_acumulado
        except Exception as e:
            print(f"Erro ao processar o arquivo {file}: {e}")
    return acumulados, files

# Função para exibir gráficos de acumulado mensal
def exibir_grafico_acumulado(df, precip_columns):
    df['Data'] = df['MesAno'].dt.to_timestamp()
    plt.figure(figsize=(10, 6))
    for col in precip_columns:
        plt.plot(df['Data'], df[col], label=col)
    plt.title("Acumulado Mensal de Precipitação")
    plt.xlabel("Data")
    plt.ylabel("Precipitação (mm)")
    plt.legend(bbox_to_anchor=(1, 1), loc='upper left')
    plt.grid()
    plt.show()

# Função para exibir gráficos de comparação anual
def exibir_grafico_comparacao_anual(df_acumulado, precip_columns):
    #print(df_acumulado)
    df_acumulado['Ano'] = df_acumulado['MesAno'].dt.year
    df_anual = df_acumulado.groupby('Ano')[precip_columns].sum().reset_index()
    plt.figure(figsize=(10, 6))
    for col in precip_columns:
        plt.bar(df_anual['Ano'], df_anual[col], label=col)
    plt.title("Acumulado Anual de Precipitação - Série Histórica")
    plt.xlabel("Ano")
    plt.ylabel("Precipitação (mm)")
    plt.legend().remove()
    plt.show()

# Função para calcular médias por estação do ano
def media_estacao(df, precip_columns):
    stations = {
        'Outono': [3, 4, 5],
        'Inverno': [6, 7, 8],
        'Primavera': [9, 10, 11],
        'Verão': [12, 1, 2],
    }
    print("Selecione uma estação do ano:")
    for i, station in enumerate(stations.keys(), start=1):
        print(f"{i}. {station}")
    
    station_index = int(input("Digite o número da estação escolhida: ")) - 1

    try:
        station_selected = list(stations.keys())[station_index]
        meses = stations[station_selected]
    except Exception as e:
        print("Escolha inválida")

    else:
        df['Ano'] = df['MesAno'].dt.year
        df['Mes'] = df['MesAno'].dt.month
        df_station = df[df['Mes'].isin(meses)]
        df_station_avg = df_station.groupby('Ano')[precip_columns].mean().reset_index()

        plt.figure(figsize=(10, 6))
        for col in precip_columns:
            plt.plot(df_station_avg['Ano'], df_station_avg[col], label=f"Média {col}")
        plt.title(f"Médias de Precipitação na Estação {station_selected}")
        plt.xlabel("Ano")
        plt.ylabel("Precipitação (mm)")
        plt.legend().remove()
        plt.grid()
        plt.show()

# Função para calcular acumulados por estação do ano
def acumulado_estacao(df, precip_columns):
    stations = {
        'Outono': [3, 4, 5],
        'Inverno': [6, 7, 8],
        'Primavera': [9, 10, 11],
        'Verão': [12, 1, 2],
    }
    print("Selecione uma estação do ano:")
    for i, station in enumerate(stations.keys(), start=1):
        print(f"{i}. {station}")

    station_index = int(input("Digite o número da estação escolhida: ")) - 1

    try: 
        station_selected = list(stations.keys())[station_index]
        meses = stations[station_selected]
    except Exception as e:
        print("Escolha inválida")
    
    else:
        df['Ano'] = df['MesAno'].dt.year
        df['Mes'] = df['MesAno'].dt.month
        df_station = df[df['Mes'].isin(meses)]
        df_station_sum = df_station.groupby('Ano')[precip_columns].sum().reset_index()

        plt.figure(figsize=(10, 6))
        for col in precip_columns:
            plt.bar(df_station_sum['Ano'], df_station_sum[col], label=f"Acumulado {col}")
        plt.title(f"Acumulados de Precipitação na Estação {station_selected}")
        plt.xlabel("Ano")
        plt.ylabel("Precipitação (mm)")
        plt.legend().remove()
        plt.grid()
        plt.show()

def calcular_dias_chuva(files, acumulados):
    dias_chuva_mensal = []
    dias_chuva_anual = []

    for file in files:
        df_acc = acumulados[file]

        # Convertendo 'MesAno' para datetime
        df_acc['Data'] = df_acc['MesAno'].dt.to_timestamp()

        # Calculando dias de chuva: usando 'NumDiasDeChuva' se disponível, caso contrário, precipitação > 0
        if 'NumDiasDeChuva' in df_acc.columns:
            df_acc['DiasChuva'] = df_acc['NumDiasDeChuva']
        else:
            precip_columns = [col for col in df_acc.columns if col.startswith('Chuva')]
            df_acc['DiasChuva'] = (df_acc[precip_columns] > 0).sum(axis=1)

        # Dias de chuva por mês
        dias_mensais = df_acc.groupby(df_acc['Data'].dt.to_period('M'))['DiasChuva'].sum().reset_index()
        dias_mensais['Estacao'] = file.replace("_Chuvas.csv", "")
        dias_chuva_mensal.append(dias_mensais)

        # Dias de chuva por ano
        dias_anuais = df_acc.groupby(df_acc['Data'].dt.year)['DiasChuva'].sum().reset_index()
        dias_anuais['Estacao'] = file.replace("_Chuvas.csv", "")
        dias_chuva_anual.append(dias_anuais)

    return pd.concat(dias_chuva_mensal, ignore_index=True), pd.concat(dias_chuva_anual, ignore_index=True)

def plot_dias_chuva_mensal(df_dias_chuva_mensal, station_id, selected_year):
    df_filtrado = df_dias_chuva_mensal[df_dias_chuva_mensal['Estacao'] == station_id]
    df_filtrado['MesAno'] = pd.to_datetime(df_filtrado['Data'].astype(str) + '-01')
    df_filtrado = df_filtrado[df_filtrado['MesAno'].dt.year == selected_year]

    if not df_filtrado.empty:
        plt.figure(figsize=(10, 6))
        plt.bar(df_filtrado['MesAno'], df_filtrado['DiasChuva'], color='blue', alpha=0.7, width=12)
        plt.title(f"Dias de Chuva Mensais na Estação {station_id} - Ano {selected_year}")
        plt.xlabel("Mês/Ano")
        plt.ylabel("Dias de Chuva")
        plt.grid(True)
        plt.show()
    else:
        print(f"Nenhum dado disponível para o ano {selected_year}.")

# Função principal
def main():
    workspace = r"dados_chuvaANA"
    estacoes_file = r"C:\Users\davils\Documents\Lauriano\Code\Arcpy\Victor\estacoes_rj.csv"
    acumulados, files = carregar_dados(workspace, estacoes_file)

    station_ids = [f.replace("_Chuvas.csv", "") for f in files]
    print("Estações disponíveis:")
    num_por_linha = 4
    for i in range(0, len(station_ids), num_por_linha):
        linha = station_ids[i:i + num_por_linha]
        print(" | ".join(f"{j+1}. {station}" for j, station in enumerate(linha, start=i)))

    while True:
        escolha = int(input("Escolha uma estação pelo número (ou 0 para sair): ")) - 1
        if escolha == -1:
            break
        if escolha < 0 or escolha >= len(station_ids):
            print("Escolha inválida!")
            continue

        station_id = station_ids[escolha]
        df = acumulados[f"{station_id}_Chuvas.csv"]
        precip_columns = [col for col in df.columns if col.startswith('Chuva')]

        # Calculando dias de chuva
        df_dias_chuva_mensal, df_dias_chuva_anual = calcular_dias_chuva(files, acumulados)

        print("\nOpções de gráficos:")
        print("1. Gráfico de acumulado mensal")
        print("2. Comparação anual de acumulados")
        print("3. Gráfico de médias de precipitação por estação")
        print("4. Gráfico de acumulado por estação")
        print("5. Gráfico de dias de chuva por estação e ano")
        escolha_grafico = int(input("Escolha uma opção: "))

        if escolha_grafico == 0:
            break
        if escolha_grafico == 1:
            exibir_grafico_acumulado(df, precip_columns)
        elif escolha_grafico == 2:
            exibir_grafico_comparacao_anual(acumulados, precip_columns)
        elif escolha_grafico == 3:
            media_estacao(df, precip_columns)
        elif escolha_grafico == 4:
            acumulado_estacao(df, precip_columns)
        elif escolha_grafico == 5:
            selected_year = int(input("Digite o ano desejado: "))
            if selected_year == 0:
                break
            if selected_year < 2000 or selected_year > 2024:
                print("Ano inválido!")
                continue
            try:
                plot_dias_chuva_mensal(df_dias_chuva_mensal, station_id, selected_year)
            except Exception as e:
                print("Escolha inválida")
        else:
            print("Escolha inválida!")

main()