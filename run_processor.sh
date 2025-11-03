#!/bin/bash

# ========================================
# Intexta Document Processor - Launcher
# ========================================

echo ""
echo "========================================"
echo "  Intexta Document Processor"
echo "========================================"
echo ""

show_menu() {
    echo "Selecciona el modo de operación:"
    echo ""
    echo "  1. Modo Escucha (Listen) - Continuo"
    echo "  2. Procesar Pendientes - Una vez"
    echo "  3. Reprocesar Documento"
    echo "  4. Ver Ayuda"
    echo "  5. Salir"
    echo ""
}

listen_mode() {
    echo ""
    read -p "Intervalo en segundos (default: 30): " interval
    interval=${interval:-30}
    
    echo ""
    echo "Iniciando modo escucha con intervalo de $interval segundos..."
    echo "Presiona Ctrl+C para detener"
    echo ""
    
    python3 document_processor.py --mode listen --interval $interval
}

process_mode() {
    echo ""
    echo "Procesando documentos pendientes..."
    echo ""
    
    python3 document_processor.py --mode process-pending
    
    echo ""
    read -p "Presiona Enter para continuar..."
}

reprocess_mode() {
    echo ""
    read -p "Ingresa el ID del documento: " docid
    
    if [ -z "$docid" ]; then
        echo "Error: Debes proporcionar un ID de documento"
        read -p "Presiona Enter para continuar..."
        return
    fi
    
    echo ""
    echo "Reprocesando documento: $docid"
    echo ""
    
    python3 document_processor.py --mode reprocess --doc-id $docid
    
    echo ""
    read -p "Presiona Enter para continuar..."
}

help_mode() {
    echo ""
    python3 document_processor.py --help
    echo ""
    read -p "Presiona Enter para continuar..."
}

# Menú principal
while true; do
    show_menu
    read -p "Ingresa tu opción (1-5): " choice
    
    case $choice in
        1)
            listen_mode
            ;;
        2)
            process_mode
            ;;
        3)
            reprocess_mode
            ;;
        4)
            help_mode
            ;;
        5)
            echo ""
            echo "Saliendo..."
            exit 0
            ;;
        *)
            echo "Opción inválida. Intenta de nuevo."
            sleep 1
            ;;
    esac
    
    clear
done
