import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from config import MODO_EXTRACCION, CONFIGURACION, DELAY_ENTRE_REQUESTS

def get_runner_details(bib_number, session, base_url):
    """
    Obtiene los detalles de un corredor específico, incluyendo sus tiempos parciales.
    """
    detail_url = f"{base_url}/detail.php"
    form_data = {'d_number': bib_number}
    
    # Headers más completos para simular un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Referer': f"{base_url}/index.php",
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Pausa antes de cada intento
            if attempt > 0:
                wait_time = 5 * (2 ** attempt)  # Backoff exponencial: 5, 10, 20 segundos
                print(f"  ⏳ Reintentando en {wait_time} segundos... (intento {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            
            response = session.post(detail_url, data=form_data, headers=headers, timeout=30)
            
            if response.status_code == 403:
                print(f"  🚫 Error 403 para BIB {bib_number} (intento {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    print(f"  ❌ Servidor bloqueó BIB {bib_number} después de {max_retries} intentos")
                    return None
                continue
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Debug: guardar la primera respuesta para análisis
            if bib_number == '4':  # Solo para el primer corredor
                with open('runner_detail_debug.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Debug: Guardado detalle del corredor {bib_number} en runner_detail_debug.html")

            # Extraer datos básicos del corredor
            runner_data = {'BIB': bib_number}
            
            # Buscar tablas con información
            tables = soup.find_all('table', class_='m-item_tbl')
            print(f"Debug: Encontradas {len(tables)} tablas para BIB {bib_number}")
            
            if not tables:
                print(f"Debug: No se encontraron tablas para BIB {bib_number}")
                return None

            # Procesar la primera tabla (posición, BIB, nombre)
            if len(tables) > 0:
                first_table = tables[0]
                data_row = None
                for row in first_table.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) == 3 and cols[1].text.strip() == str(bib_number):
                        runner_data['posicion'] = cols[0].text.strip()
                        runner_data['BIB'] = cols[1].text.strip()
                        runner_data['Nombre'] = cols[2].text.strip().replace('／', ' / ')
                        break

            # Procesar la segunda tabla (información detallada)
            if len(tables) > 1:
                info_table = tables[1]
                for row in info_table.find_all('tr'):
                    cols = row.find_all('td')
                    th_element = row.find('th')
                    
                    if th_element and len(cols) >= 1:
                        th = th_element.text.strip()
                        td = cols[0].text.strip()
                        
                        # Mapear campos específicos
                        if '参加種目' in th or 'Race Category' in th:
                            runner_data['categoria'] = td
                            # Filtro: Solo procesar Marathon Men y Marathon Women
                            if 'Wheelchair' in td or 'Junior' in td or '車いす' in td or 'ジュニア' in td or '知的障がい' in td or '視覚障がい' in td or '移植者' in td:
                                print(f"Debug: Saltando corredor BIB {bib_number} - Categoría: {td}")
                                return None
                        elif '年齢' in th or 'Age' in th:
                            runner_data['Edad'] = td
                        elif '性別' in th or 'Sex' in th:
                            runner_data['Genero'] = td
                        elif '国籍' in th or 'Nationality' in th:
                            runner_data['Nacionalidad'] = td
                        elif 'タイム(ネット)' in th or 'Time (net)' in th:
                            runner_data['tiempo_neto'] = td
                        elif 'タイム(グロス)' in th or 'Time (gross)' in th:
                            runner_data['tiempo_oficial'] = td

            # Procesar tablas de tiempos parciales (tabla 3 específicamente)
            if len(tables) > 2:
                splits_table = tables[2]  # La tercera tabla contiene los splits
                print(f"Debug: Procesando tabla de splits (tabla 3)")
                
                # Extraer el HTML completo de la tabla para análisis
                table_html = str(splits_table)
                
                # Usar regex para extraer los tiempos de manera más precisa
                import re
                
                # Patrón para 5km (más flexible con espacios en blanco)
                match_5km = re.search(r'<td[^>]*class="taR"[^>]*>5km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_5km and not runner_data.get('parcial_5km'):
                    runner_data['parcial_5km'] = match_5km.group(1)
                    print(f"Debug: 5km = {match_5km.group(1)}")
                
                # Patrón para 10km
                match_10km = re.search(r'<td[^>]*class="taR"[^>]*>10km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_10km and not runner_data.get('parcial_10km'):
                    runner_data['parcial_10km'] = match_10km.group(1)
                    print(f"Debug: 10km = {match_10km.group(1)}")
                
                # Patrón para 15km
                match_15km = re.search(r'<td[^>]*class="taR"[^>]*>15km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_15km and not runner_data.get('parcial_15km'):
                    runner_data['parcial_15km'] = match_15km.group(1)
                    print(f"Debug: 15km = {match_15km.group(1)}")
                
                # Patrón para 20km
                match_20km = re.search(r'<td[^>]*class="taR"[^>]*>20km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_20km and not runner_data.get('parcial_20km'):
                    runner_data['parcial_20km'] = match_20km.group(1)
                    print(f"Debug: 20km = {match_20km.group(1)}")
                
                # Patrón para Halfway Point
                match_halfway = re.search(r'<td[^>]*class="taR"[^>]*>中間点／Halfway Point</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_halfway and not runner_data.get('medio_maraton'):
                    runner_data['medio_maraton'] = match_halfway.group(1)
                    print(f"Debug: Halfway = {match_halfway.group(1)}")
                
                # Patrón para 25km
                match_25km = re.search(r'<td[^>]*class="taR"[^>]*>25km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_25km and not runner_data.get('parcial_25km'):
                    runner_data['parcial_25km'] = match_25km.group(1)
                    print(f"Debug: 25km = {match_25km.group(1)}")
                
                # Patrón para 30km
                match_30km = re.search(r'<td[^>]*class="taR"[^>]*>30km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_30km and not runner_data.get('parcial_30km'):
                    runner_data['parcial_30km'] = match_30km.group(1)
                    print(f"Debug: 30km = {match_30km.group(1)}")
                
                # Patrón para 35km
                match_35km = re.search(r'<td[^>]*class="taR"[^>]*>35km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_35km and not runner_data.get('parcial_35km'):
                    runner_data['parcial_35km'] = match_35km.group(1)
                    print(f"Debug: 35km = {match_35km.group(1)}")
                
                # Patrón para 40km
                match_40km = re.search(r'<td[^>]*class="taR"[^>]*>40km</td>\s*<td[^>]*class="taC"[^>]*>([0-9:]+)</td>', table_html)
                if match_40km and not runner_data.get('parcial_40km'):
                    runner_data['parcial_40km'] = match_40km.group(1)
                    print(f"Debug: 40km = {match_40km.group(1)}")

            print(f"Debug: Datos extraídos para BIB {bib_number}: {list(runner_data.keys())}")
            return runner_data
            
        except requests.RequestException as e:
            print(f"  ⚠️  Error de conexión para BIB {bib_number} (intento {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print(f"  ❌ Falló BIB {bib_number} después de {max_retries} intentos")
                return None
        except Exception as e:
            print(f"  ⚠️  Error inesperado para BIB {bib_number} (intento {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print(f"  ❌ Falló BIB {bib_number} después de {max_retries} intentos")
                return None
    
    return None

def main():
    base_url = "https://www.marathon.tokyo/2024/result"
    index_url = f"{base_url}/index.php"
    session = requests.Session()
    all_runners_data = []
    total_athletes_processed = 0  # Contador global de atletas procesados
    start_time = time.time()  # Tiempo de inicio para cálculos de velocidad

    # Obtener configuración del modo seleccionado
    config = CONFIGURACION[MODO_EXTRACCION]
    print(f"🎯 {config['descripcion']}")

    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': base_url,
        'Origin': 'https://www.marathon.tokyo',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        # 1. Primero hacer GET para obtener la página inicial y establecer cookies
        print("Obteniendo página inicial...")
        initial_response = session.get(base_url, headers=headers)
        initial_response.raise_for_status()
        
        # 2. Hacer POST a index.php (como indica el action del form)
        print("Enviando formulario de búsqueda...")
        form_data = {
            'category': '',
            'number': '',
            'name': '',
            'age': '',
            'sex[]': '',
            'country': '',
            'prefecture': '',
            'sort_key': 'place',
            'sort_asc': '1',
            'page': '1',
            'd_number': ''
        }
        
        response = session.post(index_url, data=form_data, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer el número total de páginas (con manejo de errores)
        pager_div = soup.find('div', class_='fnav pager')
        if not pager_div:
            print("Error: No se encontró la sección de paginación.")
            print("Intentando buscar elementos de resultados en la página...")
            
            # Verificar si hay una tabla de resultados
            results_table = soup.find('table', class_='m-item_tbl mb10')
            if results_table:
                print("Se encontró una tabla de resultados. Procesando...")
                # Extraer información de paginación del texto
                page_info = soup.find('p', class_='taR')
                if page_info and '／' in page_info.text:
                    total_runners = int(page_info.text.split('／')[-1])
                    total_pages = (total_runners // 50) + 1
                    print(f"Se encontraron {total_runners} corredores en {total_pages} páginas.")
                else:
                    print("No se pudo determinar el número total de páginas. Procesando solo la primera página.")
                    total_pages = 1
            else:
                print("No se encontraron resultados. Guardando el HTML en 'error_page.html'")
                with open('error_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                return
        else:
            pager_text = pager_div.find('p', class_='taR').text
            total_runners = int(pager_text.split('／')[-1])
            total_pages = (total_runners // 50) + 1
            print(f"Se encontraron {total_runners} corredores en {total_pages} páginas.")
            
            # Determinar páginas a procesar según configuración
            if config['max_pages'] is None:
                pages_to_process = total_pages
                print(f"🚀 MODO COMPLETO: Procesando todas las {total_pages} páginas ({total_runners} corredores).")
                print(f"⏱️  Tiempo estimado: {total_runners * 1.5 / 3600:.1f} horas")
            else:
                pages_to_process = min(config['max_pages'], total_pages)
                estimated_runners = pages_to_process * (config['max_runners_per_page'] or 50)
                print(f"🧪 MODO PRUEBA: Procesando {pages_to_process} de {total_pages} páginas (~{estimated_runners} corredores máximo).")
            
            print(f"📊 Progreso se mostrará cada atleta consultado...")

        # 2. Iterar a través de las páginas de resultados
        for page_num in range(1, pages_to_process + 1):
            print(f"\nProcesando página de resultados {page_num}/{pages_to_process}...")
            
            # Para la primera página, usar la respuesta que ya tenemos
            if page_num == 1:
                page_soup = soup
            else:
                form_data = {
                    'category': '',
                    'number': '',
                    'name': '',
                    'age': '',
                    'sex[]': '',
                    'country': '',
                    'prefecture': '',
                    'sort_key': 'place',
                    'sort_asc': '1',
                    'page': str(page_num),
                    'd_number': ''
                }
                page_response = session.post(index_url, data=form_data, headers=headers)
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
            
            # Extraer los BIB numbers de la tabla de la página actual
            bib_numbers = []
            results_table = page_soup.find('table', class_='m-item_tbl mb10')
            if results_table:
                for row in results_table.find_all('tr')[1:]:
                    link = row.find('a', href=lambda href: href and 'javascript:detail' in href)
                    if link:
                        match = re.search(r"javascript:detail\('(\d+)'\);", link['href'])
                        if match:
                            bib_numbers.append(match.group(1))
            
            # Aplicar límite de corredores por página si está configurado
            if config['max_runners_per_page'] is not None:
                bib_numbers = bib_numbers[:config['max_runners_per_page']]
            
            print(f"Encontrados {len(bib_numbers)} corredores en esta página. Obteniendo detalles...")

            # 3. Para cada BIB, obtener los detalles completos
            for i, bib in enumerate(bib_numbers):
                total_athletes_processed += 1
                
                # Calcular porcentaje dinámicamente
                if config['max_pages'] is None:
                    # Modo completo: usar total real de corredores
                    percentage = (total_athletes_processed / total_runners) * 100
                    total_text = str(total_runners)
                else:
                    # Modo prueba: calcular estimado
                    estimated_total = pages_to_process * (config['max_runners_per_page'] or 50)
                    percentage = (total_athletes_processed / estimated_total) * 100 if estimated_total > 0 else 0
                    total_text = f"~{estimated_total}"
                
                print(f"Consultando atleta {total_athletes_processed} de {total_text} ({percentage:.2f}%) - Página {page_num}/{pages_to_process} - Corredor {i+1}/{len(bib_numbers)} - BIB: {bib}")
                details = get_runner_details(bib, session, base_url)
                if details:
                    print(f"  ✅ Datos extraídos para BIB: {details.get('BIB', bib)}")
                    all_runners_data.append(details)
                else:
                    print(f"  ❌ No se pudieron extraer datos para BIB: {bib}")
                
                # Resumen de progreso (cada 50 en prueba, cada 100 en completo)
                progress_interval = 50 if config['max_pages'] is not None else 100
                if total_athletes_processed % progress_interval == 0:
                    valid_runners = len(all_runners_data)
                    elapsed_time = time.time() - start_time
                    rate = total_athletes_processed / elapsed_time if elapsed_time > 0 else 0
                    
                    print(f"\n📈 RESUMEN PROGRESO:")
                    print(f"   🔍 Atletas consultados: {total_athletes_processed}")
                    print(f"   ✅ Datos válidos extraídos: {valid_runners}")
                    print(f"   📊 Porcentaje completado: {percentage:.2f}%")
                    print(f"   ⚡ Velocidad: {rate:.2f} atletas/segundo")
                    print(f"   ⏱️  Tiempo transcurrido: {elapsed_time/3600:.2f} horas")
                    
                    # Solo mostrar ETA en modo completo
                    if config['max_pages'] is None:
                        remaining_athletes = total_runners - total_athletes_processed
                        eta_seconds = remaining_athletes / rate if rate > 0 else 0
                        eta_hours = eta_seconds / 3600
                        print(f"   🎯 Tiempo estimado restante: {eta_hours:.2f} horas")
                    print()
                
                time.sleep(DELAY_ENTRE_REQUESTS) # Pausa configurable

    except requests.RequestException as e:
        print(f"Error al hacer la petición principal: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

    # 4. Guardar todos los datos en un archivo CSV
    if all_runners_data:
        total_time = time.time() - start_time
        mode_text = "PRUEBA" if config['max_pages'] is not None else "COMPLETA"
        
        print(f"\n🎯 EXTRACCIÓN {mode_text} COMPLETADA")
        print(f"📊 Atletas consultados: {total_athletes_processed}")
        print(f"✅ Datos válidos extraídos: {len(all_runners_data)}")
        print(f"❌ Atletas descartados (wheelchair/junior): {total_athletes_processed - len(all_runners_data)}")
        print(f"⏱️  Tiempo total: {total_time/3600:.2f} horas")
        print(f"⚡ Velocidad promedio: {total_athletes_processed/total_time:.2f} atletas/segundo")
        
        # Nombre de archivo dinámico según el modo
        if config['max_pages'] is not None:
            filename = f'marathon_tokyo_results_2024_{MODO_EXTRACCION}.csv'
        else:
            filename = 'marathon_tokyo_results_2024_completo.csv'
            
        print(f"📁 Guardando todos los datos en '{filename}'...")
        df = pd.DataFrame(all_runners_data)
        
        column_order = ["BIB", "Nombre", "Nacionalidad", "Genero", "Edad", "tiempo_oficial",
                        "parcial_5km", "parcial_10km", "parcial_15km", "parcial_20km", 
                        "medio_maraton", "parcial_25km", "parcial_30km", "parcial_35km", "parcial_40km"]
        
        for col in column_order:
            if col not in df.columns:
                df[col] = None
        
        df = df.reindex(columns=column_order)
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"¡Extracción {mode_text.lower()} completada con éxito!")
        print(f"📋 Archivo guardado: {filename}")
    else:
        print("No se pudo extraer ningún dato. Revisa el script o la página web.")

if __name__ == "__main__":
    main()

