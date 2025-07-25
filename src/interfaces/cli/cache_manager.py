"""
Cache Manager - Gestión y estadísticas de caché OCR.
"""

from infrastructure import logger, ocr_cache


def show_cache_stats() -> None:
    """Muestra estadísticas de la caché OCR."""
    print("\nObteniendo estadísticas de caché...")
    try:
        stats = ocr_cache.get_stats()
        print("\n=== Estadísticas de Caché OCR ===")
        print("-" * 40)
        print(f"Total de entradas: {stats.get('total_entries', 0)}")

        size_kb = stats.get('total_text_size_bytes', 0) / 1024
        print(f"Tamaño aproximado: {size_kb:.2f} KB")

        last_update = stats.get('last_update', 'Nunca')
        print(f"Última actualización: {last_update}")

        memory_size = stats.get('memory_cache_size', 0)
        print(f"Caché en memoria: {memory_size} entradas")

        if stats.get('total_entries', 0) > 0:
            print("[INFO] La caché está optimizando el rendimiento del OCR")
        else:
            print("[INFO] La caché está vacía - se poblará con el uso")

    except Exception as e:
        logger.exception("Error obteniendo estadísticas de caché")
        print(f"[ERROR] Error al obtener estadísticas: {e}")
        print("Revisa los logs para más detalles")


def clear_cache() -> None:
    """Limpia la caché OCR."""
    print("\nLimpiando caché OCR...")
    try:
        ocr_cache.clear_cache(memory_only=False)
        print("[✓] Caché limpiada exitosamente")
    except Exception as e:
        logger.exception("Error limpiando caché")
        print(f"[ERROR] Error al limpiar caché: {e}")


def optimize_cache() -> None:
    """Optimiza la caché OCR."""
    print("\nOptimizando caché OCR...")
    try:
        # Eliminar entradas antiguas o duplicadas
        stats_before = ocr_cache.get_stats()
        ocr_cache.vacuum_database()
        stats_after = ocr_cache.get_stats()

        print(f"[✓] Caché optimizada exitosamente")
        print(f"    Entradas antes: {stats_before.get('total_entries', 0)}")
        print(f"    Entradas después: {stats_after.get('total_entries', 0)}")
        print(
            f"    Espacio recuperado: {(stats_before.get('total_text_size_bytes', 0) - stats_after.get('total_text_size_bytes', 0))/1024:.2f} KB")
    except Exception as e:
        logger.exception("Error optimizando caché")
        print(f"[ERROR] Error al optimizar caché: {e}")


def show_cache_menu() -> None:
    """Muestra un menú de gestión de caché."""
    while True:
        print("\n=== Gestión de Caché OCR ===")
        print("1. Mostrar estadísticas")
        print("2. Limpiar caché")
        print("3. Optimizar caché")
        print("4. Volver al menú principal")

        choice = input("\nSeleccione una opción (1-4): ").strip()

        match choice:
            case "1":
                show_cache_stats()
            case "2":
                confirm = input(
                    "¿Está seguro de limpiar la caché? (s/N): ").strip().lower()
                if confirm == 's':
                    clear_cache()
                else:
                    print("Operación cancelada")
            case "3":
                optimize_cache()
            case "4":
                break
            case _:
                print("[ERROR] Opción inválida")
