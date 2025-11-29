# # -*- coding: utf-8 -*-
# # Minimalna aplikacja Streamlit — tylko 4 stacje: Zatwarnica, Kalnica, Dwernik, Stuposiany
#
# import streamlit as st
# from datetime import datetime
# from flood_monitoring.ui.components.charts import display_station_charts
# from flood_monitoring.ui.components.map import display_map
# from flood_monitoring.ui.services.api_service import get_station_data, get_stations
#
# # -------------------------
# # Funkcje pomocnicze (proste)
# # -------------------------
#
# def get_wojewodztwo(props: dict) -> str:
#     return props.get("wojewodztwo", props.get("wojewodztwo:", ""))
#
# def get_rzeka(props: dict) -> str:
#     return props.get("rzeka")
#
# def get_stacja(props: dict) -> str:
#     return props.get("stacja")
#
#
# def format_last_update(props: dict) -> str:
#     """Stara się sparsować datę z właściwości i zwrócić ładny string."""
#     for key in ("stan_wody_data_pomiaru", "przeplyw_data", "data"):
#         val = props.get(key)
#         if not val:
#             continue
#         try:
#             dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
#             return dt.strftime("%Y-%m-%d %H:%M")
#         except Exception:
#             return str(val)
#     return "Brak danych"
#
#
# # -------------------------
# # Główna funkcja aplikacji
# # -------------------------
#
# def show_hydro_stations():
#     # st.set_page_config(page_title="Stacje pomiarowe — minimalnie", layout="wide")
#     st.title("Stacje pomiarowe — tylko wybrane")
#     st.markdown(
#         "Zatwarnica, Kalnica, Dwernik, Stuposiany. "
#     )
#
#     # Prosty stały zakres czasowy (możesz zmienić wartość jeśli chcesz)
#     days_back = 1
#     # Prosty toggle wydajności (można zostawić domyślnie True)
#     use_progressive_loading = True
#     batch_size = 100
#
#     # Prosty cache w sesji
#     if 'stations_cache' not in st.session_state:
#         st.session_state.stations_cache = {}
#
#     # Pobieramy listę stacji z API
#     stations = get_stations()
#     if not stations:
#         st.error("❌ Nie udało się pobrać danych stacji z serwera.")
#         return
#
#     # Filtrujemy tylko 4 wybrane stacje
#     allowed_names = {"Zatwarnica", "Kalnica", "Dwernik", "Stuposiany"}
#     stations = [s for s in stations if s.get("properties", {}).get("stacja") in allowed_names]
#
#     if not stations:
#         st.warning("Brak danych dla wybranych stacji: Zatwarnica, Kalnica, Dwernik, Stuposiany")
#         return
#
#     # Nagłówki metryk (proste)
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("Stacje (pokazane)", len(stations))
#     with col2:
#         active_count = sum(1 for s in stations if s["properties"].get("status") != "inactive")
#         st.metric("✅ Aktywne", active_count)
#     with col3:
#         provinces = len(set(get_wojewodztwo(s["properties"]) for s in stations if get_wojewodztwo(s["properties"])))
#         st.metric("Województwa (unikat)", provinces)
#     with col4:
#         rivers = len(set(get_rzeka(s["properties"]) for s in stations if get_rzeka(s["properties"])))
#         st.metric("Rzeki (unikat)", rivers)
#
#     st.markdown("---")
#
#     # Przygotowanie danych do mapy (upraszczamy format)
#     enhanced_stations = []
#     for s in stations:
#         props = s.get("properties", {})
#         coords = s.get("geometry", {}).get("coordinates", [None, None])
#         lon = float(coords[0]) if coords and coords[0] is not None else None
#         lat = float(coords[1]) if coords and coords[1] is not None else None
#
#         stan_wody_display = "Brak danych"
#         if props.get('stan_wody') is not None:
#             try:
#                 stan_wody_display = f"{float(props['stan_wody']):.1f} cm"
#             except Exception:
#                 stan_wody_display = str(props.get('stan_wody'))
#
#         przeplyw_display = "Brak danych"
#         if props.get('przeplyw') is not None:
#             try:
#                 przeplyw_display = f"{float(props['przeplyw']):.2f} m³/s"
#             except Exception:
#                 przeplyw_display = str(props.get('przeplyw'))
#
#         enhanced_stations.append({
#             "lat": lat,
#             "lon": lon,
#             "name": get_stacja(props),
#             "river": get_rzeka(props) or "Nieznana rzeka",
#             "code": props.get("id_stacji", "N/A"),
#             "wojewodztwo": get_wojewodztwo(props) or "Nieznane",
#             "status": props.get("status", "active"),
#             "ostatnia_aktualizacja": format_last_update(props),
#             "stan_wody": stan_wody_display,
#             "przeplyw": przeplyw_display
#         })
#
#     # Wyświetlamy mapę (funkcja z Twojego projektu)
#     display_map(
#         stations_data=enhanced_stations,
#         map_style="OpenStreetMap",
#         cluster_markers=False,
#         responsive=True
#     )
#
#     st.markdown("### Szczegóły stacji")
#     # Tabela szczegółów
#     table_data = []
#     for s in stations:
#         props = s.get("properties", {})
#         coords = s.get("geometry", {}).get("coordinates", [None, None])
#         table_data.append({
#             "Stacja": get_stacja(props),
#             "Rzeka": get_rzeka(props) or "Nieznana",
#             "Województwo": get_wojewodztwo(props) or "Nieznane",
#             "Współrzędne": f"{coords[1]:.4f}, {coords[0]:.4f}" if coords and coords[0] is not None and coords[1] is not None else "Brak",
#             "ID": props.get("id_stacji", "N/A"),
#             "Ostatnia aktualizacja": format_last_update(props)
#         })
#     st.dataframe(table_data, use_container_width=True)
#
#     st.markdown("---")
#     # st.header("Analiza danych hydrologicznych (automatycznie dla wybranych stacji)")
#     # st.info(f"Pobierane dane za ostatnie {days_back} {'dzień' if days_back == 1 else 'dni'}")
#     #
#     # # Pobieramy dane i rysujemy wykresy dla każdej z 4 stacji (jeśli są dane)
#     # for i, s in enumerate(stations):
#     #     props = s.get("properties", {})
#     #     station_id = props.get("id_stacji")
#     #     station_name = get_stacja(props) or f"Stacja {i+1}"
#     #
#     #     with st.expander(f"{station_name} — {get_rzeka(props) or 'Nieznana rzeka'}", expanded=(i == 0)):
#     #         if not station_id:
#     #             st.error(f"Brak ID stacji dla {station_name}")
#     #             continue
#     #
#     #         cache_key = f"{station_id}_{days_back}_{use_progressive_loading}_{batch_size}"
#     #         data = st.session_state.stations_cache.get(cache_key)
#     #         if not data:
#     #             try:
#     #                 if use_progressive_loading:
#     #                     data = get_station_data(station_id, days=days_back, extended=True, limit=batch_size)
#     #                 else:
#     #                     data = get_station_data(station_id, days=days_back, extended=False, limit=batch_size)
#     #                 if data:
#     #                     st.session_state.stations_cache[cache_key] = data
#     #             except Exception as e:
#     #                 st.error(f"Błąd pobierania danych dla {station_name}: {e}")
#     #                 data = None
#     #
#     #         if data:
#     #             # display_station_charts pochodzi z Twojego projektu — wyświetli wykresy
#     #             display_station_charts(data)
#     #         else:
#     #             st.warning(f"Brak danych pomiarowych dla stacji {station_name}")
#     #
#     # st.success("Gotowe — wyświetlono stacje: Zatwarnica, Kalnica, Dwernik, Stuposiany.")
#
#
# if __name__ == "__main__":
#     show_hydro_stations()
