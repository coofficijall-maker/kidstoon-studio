#!/bin/bash
cd ~/projekti/kidstoon-studio
source env/bin/activate

while true; do
    clear
    echo "========================================="
    echo "   KIDSTOON STUDIO v4.0 (coofficijall)   "
    echo "========================================="
    echo "1) Uredi priču (prica.txt)"
    echo "2) Generiši animirani crtać (Full HD)"
    echo "3) Pošalji izmjene na GitHub"
    echo "4) Izlaz"
    echo "-----------------------------------------"
    read -p "Odaberite opciju [1-4]: " izbor

    case $izbor in
        1) nano prica.txt ;;
        2) python studio.py; read -p "Gotovo! Pritisnite Enter..." ;;
        3) git add . && git commit -m "Update studija i price" && git push; read -p "Poslano na GitHub! Pritisnite Enter..." ;;
        4) exit 0 ;;
        *) echo "Nepoznata opcija."; sleep 1 ;;
    esac
done
