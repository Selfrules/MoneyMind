"""Script to standardize transaction annotations based on patterns."""
import re

# Read file
with open('misc/transazioni_da_annotare.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Define patterns based on user annotations
patterns = [
    # Abbonamenti ricorrenti
    (r'\| ([\d-]+) \| €4\.99 \| Amazon \| Revolut \| \|', r'| \1 | €4.99 | Amazon | Revolut | Abbonamento Amazon Prime Video |'),
    (r'\| ([\d-]+) \| €19\.76 \| Google Workspace[^|]*\| Revolut \| \|', r'| \1 | €19.76 | Google Workspace | Revolut | Abbonamento Google Workspace selfrules.org |'),
    (r'\| ([\d-]+) \| €49\.00 \| Unobravo \| Revolut \| \|', r'| \1 | €49.00 | Unobravo | Revolut | Psicologa, settimanale |'),
    (r'\| ([\d-]+) \| €20\.99 \| Spotify \| Revolut \| \|', r'| \1 | €20.99 | Spotify | Revolut | Abbonamento Spotify |'),
    (r'\| ([\d-]+) \| €6\.99 \| Netflix \| Revolut \| \|', r'| \1 | €6.99 | Netflix | Revolut | Abbonamento Netflix |'),
    (r'\| ([\d-]+) \| €9\.99 \| Netflix \| Revolut \| \|', r'| \1 | €9.99 | Netflix | Revolut | Abbonamento Netflix |'),
    (r'\| ([\d-]+) \| €9\.99 \| Apple \| Revolut \| \|', r'| \1 | €9.99 | Apple | Revolut | Abbonamento iCloud |'),
    (r'\| ([\d-]+) \| €2\.99 \| Google[^|]*\| Revolut \| \|', r'| \1 | €2.99 | Google | Revolut | Abbonamento Google Drive |'),
    (r'\| ([\d-]+) \| €1\.99 \| Google One \| Revolut \| \|', r'| \1 | €1.99 | Google One | Revolut | Abbonamento Google Drive |'),
    (r'\| ([\d-]+) \| €29\.99 \| Google One \| Revolut \| \|', r'| \1 | €29.99 | Google One | Revolut | Abbonamento Google Drive annuale |'),
    (r'\| ([\d-]+) \| €28\.67 \| Notion \| Revolut \| \|', r'| \1 | €28.67 | Notion | Revolut | Abbonamento Notion mensile |'),
    (r'\| ([\d-]+) \| €109\.80 \| Anthropic \| Revolut \| \|', r'| \1 | €109.80 | Anthropic | Revolut | Abbonamento Claude mensile |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Anthropic \| Revolut \| \|', r'| \1 | €\2 | Anthropic | Revolut | Abbonamento Claude mensile |'),
    (r'\| ([\d-]+) \| €24\.40 \| Figma \| Revolut \| \|', r'| \1 | €24.40 | Figma | Revolut | Abbonamento Figma mensile |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Elevenlabs \| Revolut \| \|', r'| \1 | €\2 | Elevenlabs | Revolut | Abbonamento ElevenLabs AI |'),
    (r'\| ([\d-]+) \| €4\.99 \| Amazon Prime \| Revolut \| \|', r'| \1 | €4.99 | Amazon Prime | Revolut | Abbonamento Prime Video |'),
    (r'\| ([\d-]+) \| €4\.99 \| Prime Video \| Revolut \| \|', r'| \1 | €4.99 | Prime Video | Revolut | Abbonamento Prime Video |'),
    (r'\| ([\d-]+) \| €7\.99 \| Prime Video \| Revolut \| \|', r'| \1 | €7.99 | Prime Video | Revolut | Abbonamento Prime Video |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| GitHub \| Revolut \| \|', r'| \1 | €\2 | GitHub | Revolut | Abbonamento GitHub |'),

    # Food delivery
    (r'\| ([\d-]+) \| €([\d.]+) \| Just Eat \| Revolut \| \|', r'| \1 | €\2 | Just Eat | Revolut | Cena a domicilio |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Deliveroo \| Revolut \| \|', r'| \1 | €\2 | Deliveroo | Revolut | Cena a domicilio |'),

    # Utenze
    (r'\| ([\d-]+) \| €([\d.]+) \| Octopus Energy[^|]*\| (Revolut|Illimity) \| \|', r'| \1 | €\2 | Octopus Energy | \3 | Utenze, bolletta energia elettrica |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| TIM \| Revolut \| \|', r'| \1 | €\2 | TIM | Revolut | Utenze, telefonia e internet |'),

    # Finanziamenti
    (r'\| ([\d-]+) \| €([\d.]+) \| 202218724931422026643530190020221872493142[^|]*\| Illimity \| \|', r'| \1 | €\2 | Findomestic | Illimity | Rata finanziamento Findomestic |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| 202214930873012026643530190020221493087301[^|]*\| Illimity \| \|', r'| \1 | €\2 | Findomestic | Illimity | Rata finanziamento Findomestic |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| 202216820433692026643530190020221682043369[^|]*\| Illimity \| \|', r'| \1 | €\2 | Findomestic | Illimity | Rata finanziamento Findomestic |'),
    (r'\| ([\d-]+) \| €175\.90 \| repayment \| Revolut \| \|', r'| \1 | €175.90 | repayment | Revolut | Rata prestito Revolut |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| repayment \| Revolut \| \|', r'| \1 | €\2 | repayment | Revolut | Rata prestito Revolut |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| outstanding partial repayment \| Revolut \| \|', r'| \1 | €\2 | repayment | Revolut | Rata prestito Revolut |'),
    (r'\| ([\d-]+) \| €93\.90 \|[^|]*PR\. 77260688[^|]*\| Illimity \| \|', r'| \1 | €93.90 | Agos | Illimity | Rata finanziamento Agos |'),

    # Affitto
    (r'\| ([\d-]+) \| €550\.00 \| To Gianfranco Torricelli \| Revolut \| \|', r'| \1 | €550.00 | To Gianfranco Torricelli | Revolut | Affitto |'),

    # Trasporti
    (r'\| ([\d-]+) \| €([\d.]+) \| Tamoil \| Revolut \| \|', r'| \1 | €\2 | Tamoil | Revolut | Benzina |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| AF Petroli \| Revolut \| \|', r'| \1 | €\2 | AF Petroli | Revolut | Benzina |'),

    # Spesa alimentare
    (r'\| ([\d-]+) \| €([\d.]+) \| 9810 Spilamberto \| Revolut \| \|', r'| \1 | €\2 | Coop Spilamberto | Revolut | Spesa supermercato |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| L Isola Dei \| Revolut \| \|', r"| \1 | €\2 | L'Isola dei Sapori | Revolut | Spesa frutta e verdura |"),
    (r'\| ([\d-]+) \| €([\d.]+) \| Lisola Dei Sap \| Revolut \| \|', r"| \1 | €\2 | L'Isola dei Sapori | Revolut | Spesa frutta e verdura |"),
    (r'\| ([\d-]+) \| €([\d.]+) \| Lar E Gola \| Revolut \| \|', r'| \1 | €\2 | Lar E Gola | Revolut | Spesa macelleria |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Macelleria Lar E Gola \| Revolut \| \|', r'| \1 | €\2 | Lar E Gola | Revolut | Spesa macelleria |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Panificio Bonfiglioli \| Revolut \| \|', r'| \1 | €\2 | Panificio Bonfiglioli | Revolut | Spesa panificio |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Forno Bonfiglioli \| Revolut \| \|', r'| \1 | €\2 | Forno Bonfiglioli | Revolut | Spesa panificio |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Nespresso \| Revolut \| \|', r'| \1 | €\2 | Nespresso | Revolut | Capsule caffè |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Macelleria Lutti \| Revolut \| \|', r'| \1 | €\2 | Macelleria Lutti | Revolut | Spesa macelleria |'),

    # Gatti
    (r'\| ([\d-]+) \| €([\d.]+) \| Arcaplanet[^|]*\| Revolut \| \|', r'| \1 | €\2 | Arcaplanet | Revolut | Cibo e lettiera gatti |'),

    # Barbiere
    (r'\| ([\d-]+) \| €35\.00 \| Anymore Style Di Napol \| Revolut \| \|', r'| \1 | €35.00 | Anymore Style Di Napol | Revolut | Barbiere |'),
    (r'\| ([\d-]+) \| €30\.00 \| Anymore Style Di Napol \| Revolut \| \|', r'| \1 | €30.00 | Anymore Style Di Napol | Revolut | Barbiere |'),

    # Prelievi
    (r'\| ([\d-]+) \| €([\d.]+) \| Prelievo di contanti[^|]*\| Revolut \| \|', r'| \1 | €\2 | Prelievo contanti | Revolut | Prelievo contanti |'),

    # Videogiochi
    (r'\| ([\d-]+) \| €([\d.]+) \| Steam \| Revolut \| \|', r'| \1 | €\2 | Steam | Revolut | Videogiochi |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| gog\.com \| Revolut \| \|', r'| \1 | €\2 | GOG | Revolut | Videogiochi |'),

    # Gelato
    (r'\| ([\d-]+) \| €([\d.]+) \| Gelato \| Revolut \| \|', r'| \1 | €\2 | Gelato | Revolut | Gelato |'),

    # Paga in 3 rate
    (r'\| ([\d-]+) \| €([\d.]+) \| Paga In 3 Rate \| Revolut \| \|', r'| \1 | €\2 | Paga In 3 Rate | Revolut | Rata pagamento dilazionato |'),

    # Ristoranti/pranzo
    (r'\| ([\d-]+) \| €([\d.]+) \| Dispensa Emilia \| Revolut \| \|', r'| \1 | €\2 | Dispensa Emilia | Revolut | Pranzo fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Doppio Malto \| Revolut \| \|', r'| \1 | €\2 | Doppio Malto | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Sedimento Puglia E Ape \| Revolut \| \|', r'| \1 | €\2 | Sedimento | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Officina Della Senape \| Revolut \| \|', r'| \1 | €\2 | Officina Della Senape | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| La Stria Della Mamma D \| Revolut \| \|', r'| \1 | €\2 | La Stria Della Mamma | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Miky 2 \| Revolut \| \|', r'| \1 | €\2 | Miky 2 | Revolut | Pranzo fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Birreria Nube[^|]*\| Revolut \| \|', r'| \1 | €\2 | Birreria Nube | Revolut | Aperitivo/cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Tramvai Cremona \| Revolut \| \|', r'| \1 | €\2 | Tramvai Cremona | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Alternativo \| Revolut \| \|', r'| \1 | €\2 | Alternativo | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Box 13 14 Albani \| Revolut \| \|', r'| \1 | €\2 | Box 13 14 Albani | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Soteria Trattoria Al C \| Revolut \| \|', r'| \1 | €\2 | Soteria Trattoria | Revolut | Cena fuori |'),

    # Farmacia
    (r'\| ([\d-]+) \| €([\d.]+) \| Farmacia Violi \| Revolut \| \|', r'| \1 | €\2 | Farmacia Violi | Revolut | Farmacia |'),

    # Bar/caffè
    (r'\| ([\d-]+) \| €([\d.]+) \| Bar Le Tentazioni \| Revolut \| \|', r'| \1 | €\2 | Bar Le Tentazioni | Revolut | Caffè/colazione |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Pasticceria Manila \| Revolut \| \|', r'| \1 | €\2 | Pasticceria Manila | Revolut | Colazione/dolci |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Pasticceria Vittoria \| Revolut \| \|', r'| \1 | €\2 | Pasticceria Vittoria | Revolut | Colazione/dolci |'),
    (r"\| ([\d-]+) \| €([\d.]+) \| L'ora Del Caffe' \| Revolut \| \|", r"| \1 | €\2 | L'Ora Del Caffè | Revolut | Caffè |"),
    (r'\| ([\d-]+) \| €([\d.]+) \| Nuovo Forno Pasticceri \| Revolut \| \|', r'| \1 | €\2 | Nuovo Forno | Revolut | Colazione/dolci |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bar Prince \| Revolut \| \|', r'| \1 | €\2 | Bar Prince | Revolut | Caffè |'),

    # Tool AI
    (r'\| ([\d-]+) \| €([\d.]+) \| OpenAI \| Revolut \| \|', r'| \1 | €\2 | OpenAI | Revolut | Abbonamento ChatGPT |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Excalidraw \| Revolut \| \|', r'| \1 | €\2 | Excalidraw | Revolut | Abbonamento tool |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Squarespace \| Revolut \| \|', r'| \1 | €\2 | Squarespace | Revolut | Abbonamento hosting |'),
    (r'\| ([\d-]+) \| €10\.00 \| Gamma \| Revolut \| \|', r'| \1 | €10.00 | Gamma | Revolut | Abbonamento tool AI |'),
    (r'\| ([\d-]+) \| €10\.00 \| Komodo \| Revolut \| \|', r'| \1 | €10.00 | Komodo | Revolut | Abbonamento tool |'),

    # Viaggi
    (r'\| ([\d-]+) \| €([\d.]+) \| Booking\.com \| Revolut \| \|', r'| \1 | €\2 | Booking.com | Revolut | Viaggio/Hotel |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Trainline \| Revolut \| \|', r'| \1 | €\2 | Trainline | Revolut | Biglietto treno |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Hotel California \| Revolut \| \|', r'| \1 | €\2 | Hotel California | Revolut | Viaggio/Hotel |'),

    # Whoop
    (r'\| ([\d-]+) \| €264\.00 \| Whoop \| Revolut \| \|', r'| \1 | €264.00 | Whoop | Revolut | Abbonamento Whoop annuale |'),

    # Audible
    (r'\| ([\d-]+) \| €([\d.]+) \| Audible \| Revolut \| \|', r'| \1 | €\2 | Audible | Revolut | Abbonamento Audible |'),

    # Mensa lavoro
    (r'\| ([\d-]+) \| €([\d.]+) \| CAMST \| Revolut \| \|', r'| \1 | €\2 | CAMST | Revolut | Mensa lavoro |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Buonristoro \| Revolut \| \|', r'| \1 | €\2 | Buonristoro | Revolut | Mensa lavoro |'),

    # Aruba
    (r'\| ([\d-]+) \| €([\d.]+) \| Aruba\.it \| Revolut \| \|', r'| \1 | €\2 | Aruba | Revolut | Abbonamento hosting |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| register\.it \| Revolut \| \|', r'| \1 | €\2 | Register.it | Revolut | Abbonamento dominio |'),

    # Wise
    (r'\| ([\d-]+) \| €([\d.]+) \| Wise \| Revolut \| \|', r'| \1 | €\2 | Wise | Revolut | Trasferimento Wise |'),

    # PayPal - mappatura da storico PayPal
    (r'\| ([\d-]+) \| €9\.99 \| PayPal \| Revolut \|[^|]*\|', r'| \1 | €9.99 | Apple Services (PayPal) | Revolut | Abbonamento iCloud |'),
    (r'\| ([\d-]+) \| €17\.99 \| PayPal \| Revolut \|[^|]*\|', r'| \1 | €17.99 | Spotify (PayPal) | Revolut | Abbonamento Spotify |'),
    (r'\| ([\d-]+) \| €20\.99 \| PayPal \| Revolut \|[^|]*\|', r'| \1 | €20.99 | Spotify (PayPal) | Revolut | Abbonamento Spotify |'),
    (r'\| ([\d-]+) \| €61\.83 \| PayPal \| Revolut \|[^|]*\|', r'| \1 | €61.83 | TIM (PayPal) | Revolut | Telefono |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| PayPal \| Revolut \| \|', r'| \1 | €\2 | PayPal | Revolut | Pagamento PayPal (verificare storico) |'),

    # Odealo (videogame trading)
    (r'\| ([\d-]+) \| €([\d.]+) \| odealo\.com \| Revolut \| \|', r'| \1 | €\2 | Odealo | Revolut | Acquisto videogiochi |'),

    # Illimity bonifici
    (r'\| ([\d-]+) \| €([\d.]+) \| 200010338561[^|]*\| Illimity \| \|', r'| \1 | €\2 | Illimity | Illimity | Bonifico (DA VERIFICARE) |'),
    (r'\| ([\d-]+) \| €200\.00 \| Sacco Omar[^|]*\| Illimity \| \|', r'| \1 | €200.00 | Sacco Omar | Illimity | DA VERIFICARE |'),

    # Make (ristorante a Vignola)
    (r'\| ([\d-]+) \| €([\d.]+) \| Make \| Revolut \|[^|]*\|', r'| \1 | €\2 | Make | Revolut | Ristorante (Vignola) |'),

    # OnlyFans
    (r'\| ([\d-]+) \| €([\d.]+) \| OnlyFans \| Revolut \| \|', r'| \1 | €\2 | OnlyFans | Revolut | Abbonamento OnlyFans |'),

    # Piada
    (r'\| ([\d-]+) \| €([\d.]+) \| Piada Mare E Pineta \| Revolut \| \|', r'| \1 | €\2 | Piada Mare E Pineta | Revolut | Pranzo fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Terra Di Piada \| Revolut \| \|', r'| \1 | €\2 | Terra Di Piada | Revolut | Pranzo fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| I Panini di Mirò \| Revolut \| \|', r'| \1 | €\2 | I Panini di Mirò | Revolut | Pranzo fuori |'),

    # Arca di Noe (pet shop - gatti)
    (r'\| ([\d-]+) \| €([\d.]+) \| Arca Di Noe[^|]*\| Revolut \|[^|]*\|', r'| \1 | €\2 | Arca Di Noe | Revolut | Cibo e accessori gatti |'),

    # Nuovi pattern dalle annotazioni utente
    # Estetista
    (r'\| ([\d-]+) \| €([\d.]+) \| Simona Barbaglia \| Revolut \| \|', r'| \1 | €\2 | Simona Barbaglia | Revolut | Estetista |'),

    # Parcheggio
    (r'\| ([\d-]+) \| €([\d.]+) \| Phonzie \| Revolut \| \|', r'| \1 | €\2 | Phonzie | Revolut | Parcheggio |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Parkagent \| Revolut \| \|', r'| \1 | €\2 | Parkagent | Revolut | Parcheggio |'),

    # Ristoranti/bar vacanze
    (r'\| ([\d-]+) \| €([\d.]+) \| Il Convio \| Revolut \| \|', r'| \1 | €\2 | Il Convio | Revolut | Ristorante (vacanza) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bar La Guardiola \| Revolut \| \|', r'| \1 | €\2 | Bar La Guardiola | Revolut | Bar/spiaggia (vacanza) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bar Il Grammofono \| Revolut \| \|', r'| \1 | €\2 | Bar Il Grammofono | Revolut | Pranzo fuori (vacanza) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Il Timone \| Revolut \| \|', r'| \1 | €\2 | Il Timone | Revolut | Cena fuori (vacanza) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Ristorante Scaraboci \| Revolut \| \|', r'| \1 | €\2 | Ristorante Scaraboci | Revolut | Cena fuori (vacanza) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Sapore Di Mare \| Revolut \| \|', r'| \1 | €\2 | Sapore Di Mare | Revolut | Pranzo fuori (vacanza) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| La Brace \| Revolut \| \|', r'| \1 | €\2 | La Brace | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Chimon \| Revolut \| \|', r'| \1 | €\2 | Chimon | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bivio Enoteca \| Revolut \| \|', r'| \1 | €\2 | Bivio Enoteca | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Leglisecafe Di Turi M\. \| Revolut \| \|', r'| \1 | €\2 | Leglisecafe | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Giustospirito \| Revolut \| \|', r'| \1 | €\2 | Giustospirito | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Alleria \| Revolut \| \|', r'| \1 | €\2 | Alleria | Revolut | Cena fuori |'),
    (r"\| ([\d-]+) \| €([\d.]+) \| L'Osteria \| Revolut \| \|", r"| \1 | €\2 | L'Osteria | Revolut | Cena fuori |"),
    (r'\| ([\d-]+) \| €([\d.]+) \| Abraciami \| Revolut \| \|', r'| \1 | €\2 | Abraciami | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Enoteca Bibe Bologna \| Revolut \| \|', r'| \1 | €\2 | Enoteca Bibe | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| La Tenuta Dei Sapori S \| Revolut \| \|', r'| \1 | €\2 | La Tenuta Dei Sapori | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Pizzeria Vesuvio \| Revolut \| \|', r'| \1 | €\2 | Pizzeria Vesuvio | Revolut | Cena fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Pizza Luciano \| Revolut \| \|', r'| \1 | €\2 | Pizza Luciano | Revolut | Pranzo fuori |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Umi Sushi Ristorante S \| Revolut \| \|', r'| \1 | €\2 | Umi Sushi | Revolut | Pranzo fuori |'),
    (r"\| ([\d-]+) \| €([\d.]+) \| Ris8 Dai C'andom \| Revolut \| \|", r"| \1 | €\2 | Ris8 Dai C'andom | Revolut | Pranzo fuori |"),
    (r'\| ([\d-]+) \| €([\d.]+) \| Drogheria Delle Api Di \| Revolut \| \|', r'| \1 | €\2 | Drogheria Delle Api | Revolut | Cena fuori |'),

    # Bar/aperitivi
    (r'\| ([\d-]+) \| €([\d.]+) \| Blue Hush \| Revolut \| \|', r'| \1 | €\2 | Blue Hush | Revolut | Bar |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| The Social Hub \| Revolut \| \|', r'| \1 | €\2 | The Social Hub | Revolut | Bar |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bagno Garden Di Montal \| Revolut \| \|', r'| \1 | €\2 | Bagno Garden | Revolut | Bar (spiaggia) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bagno Sabrina \| Revolut \| \|', r'| \1 | €\2 | Bagno Sabrina | Revolut | Spiaggia (lettino/bar) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Kinotto Bar \| Revolut \| \|', r'| \1 | €\2 | Kinotto Bar | Revolut | Aperitivo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bottega Moline \| Revolut \| \|', r'| \1 | €\2 | Bottega Moline | Revolut | Aperitivo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Fermento in Villa \| Revolut \| \|', r'| \1 | €\2 | Fermento in Villa | Revolut | Aperitivo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Gafiubar \| Revolut \| \|', r'| \1 | €\2 | Gafiubar | Revolut | Aperitivo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bar Mediopadana \| Revolut \| \|', r'| \1 | €\2 | Bar Mediopadana | Revolut | Colazione |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Pompi Ginger \| Revolut \| \|', r'| \1 | €\2 | Pompi Ginger | Revolut | Caffè |'),
    (r"\| ([\d-]+) \| €([\d.]+) \| Caffe' Garden Di Mous\. \| Revolut \| \|", r"| \1 | €\2 | Caffe' Garden | Revolut | Bar |"),
    (r"\| ([\d-]+) \| €([\d.]+) \| Alfonso D'arienzo \| Revolut \| \|", r"| \1 | €\2 | Alfonso D'arienzo | Revolut | Bar |"),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bar N\. 2 \| Revolut \| \|', r'| \1 | €\2 | Bar N. 2 | Revolut | Bar |'),

    # Gelaterie
    (r'\| ([\d-]+) \| €([\d.]+) \| La Crema Di Bologna \| Revolut \| \|', r'| \1 | €\2 | La Crema Di Bologna | Revolut | Gelateria |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Gelateria Mauritius \| Revolut \| \|', r'| \1 | €\2 | Gelateria Mauritius | Revolut | Gelato |'),

    # Eventi/intrattenimento
    (r'\| ([\d-]+) \| €([\d.]+) \| DICE \| Revolut \| \|', r'| \1 | €\2 | DICE | Revolut | Concerto/evento |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Xceed \| Revolut \| \|', r'| \1 | €\2 | Xceed | Revolut | Biglietti evento |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bowling Modena \| Revolut \| \|', r'| \1 | €\2 | Bowling Modena | Revolut | Bowling/aperitivo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Bowling Sottosopra \| Revolut \| \|', r'| \1 | €\2 | Bowling Sottosopra | Revolut | Bowling |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Kinema Srl Castelfra \| Revolut \| \|', r'| \1 | €\2 | Kinema | Revolut | Bar piscina |'),

    # Terme/benessere
    (r'\| ([\d-]+) \| €([\d.]+) \| Floriba S\.r\.l\. \| Revolut \| \|', r'| \1 | €\2 | Terme Asmana | Revolut | Terme |'),

    # Trasferimenti a persone
    (r'\| ([\d-]+) \| €([\d.]+) \| manuel\.colombo \| Revolut \| \|', r'| \1 | €\2 | manuel.colombo | Revolut | Pagamento giardiniere |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| gioia\.lamberti \| Revolut \| \|', r'| \1 | €\2 | gioia.lamberti | Revolut | Regalo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| alberto\.cere \| Revolut \| \|', r'| \1 | €\2 | alberto.cere | Revolut | Donazione evento |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Chibagni \| Revolut \| \|', r'| \1 | €\2 | Chibagni | Revolut | Regalo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| To Chiedi a Stefano[^|]* \| Revolut \| \|', r'| \1 | €\2 | Stefano | Revolut | Riparazione PC |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Paola \| Revolut \| \|', r'| \1 | €\2 | Paola | Revolut | Spesa minore |'),

    # Vestiti/shopping
    (r'\| ([\d-]+) \| €([\d.]+) \| Sp Fincut Men \| Revolut \| \|', r'| \1 | €\2 | Sp Fincut Men | Revolut | Vestiti |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Gutteridge G069 \| Revolut \| \|', r'| \1 | €\2 | Gutteridge | Revolut | Vestiti |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Civico 12 Spilamberto \| Revolut \| \|', r'| \1 | €\2 | Civico 12 | Revolut | Vestiti/regalo |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Ethical Grace \| Revolut \| \|', r'| \1 | €\2 | Ethical Grace | Revolut | Shampo solido |'),

    # Incontri/dating
    (r'\| ([\d-]+) \| €([\d.]+) \| Vtsup\.com \| Revolut \| \|', r'| \1 | €\2 | Vtsup | Revolut | Sito incontri |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Seminatore44 \| Revolut \| \|', r'| \1 | €\2 | Seminatore44 | Revolut | Contenuto adulti |'),

    # Spiaggia pranzo
    (r'\| ([\d-]+) \| €([\d.]+) \| Bagni 29 30 31 Playa T \| Revolut \| \|', r'| \1 | €\2 | Bagni Playa | Revolut | Pranzo spiaggia |'),

    # Utenze Illimity (Hera SDD ~€85-100)
    (r'\| ([\d-]+) \| €((8|9)\d\.\d+) \| Illimity \| Illimity \| Bonifico \(DA VERIFICARE\) \|', r'| \1 | €\2 | Hera | Illimity | SDD Hera utenze gas/acqua/rifiuti |'),

    # Regali
    (r'\| ([\d-]+) \| €([\d.]+) \| Sp Creative Lab \| Revolut \| \|', r'| \1 | €\2 | Sp Creative Lab | Revolut | Regalo |'),

    # Veterinario Robin
    (r'\| ([\d-]+) \| €([\d.]+) \| Clínica Veterinaria Zarpas y Bigotes \| VETERINARIO \| \|', r'| \1 | €\2 | Clínica Veterinaria Zarpas y Bigotes | VETERINARIO | Cure veterinarie Robin |'),

    # Amazon (casa/cura personale)
    (r'\| ([\d-]+) \| €([\d.]+) \| Amazon \| Revolut \| \|', r'| \1 | €\2 | Amazon | Revolut | Acquisto casa/cura personale |'),

    # Vacanza Elba (agosto 2025)
    (r'\| ([\d-]+) \| €([\d.]+) \| Bar Seccheto \| Revolut \| \|', r'| \1 | €\2 | Bar Seccheto | Revolut | Bar spiaggia (vacanza Elba) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Oglasa \| Revolut \| \|', r'| \1 | €\2 | Oglasa | Revolut | Traghetto/vino (vacanza Elba) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Pv4576 \| Revolut \| \|', r'| \1 | €\2 | POS Elba | Revolut | Spesa vacanza Elba |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Prb \| Revolut \| \|', r'| \1 | €\2 | PRB | Revolut | Spesa vacanza Elba |'),

    # Locali Bologna
    (r'\| ([\d-]+) \| €([\d.]+) \| Circolo Culturale Kali \| Revolut \| \|', r'| \1 | €\2 | Circolo Kali | Revolut | Locale/drinks (Bologna) |'),

    # Google Workspace (importo variabile)
    (r'\| ([\d-]+) \| €([\d.]+) \| Google Workspace \| Revolut \| \|', r'| \1 | €\2 | Google Workspace | Revolut | Abbonamento Google Workspace |'),

    # Altro (da qualificare)
    (r'\| ([\d-]+) \| €([\d.]+) \| Bp Private Club Ente D \| Revolut \| \|', r'| \1 | €\2 | Bp Private Club | Revolut | Altro |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Sp Gabriele Santoro \| Revolut \| \|', r'| \1 | €\2 | Sp Gabriele Santoro | Revolut | Altro |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Soncini E Santunione S \| Revolut \| \|', r'| \1 | €\2 | Soncini E Santunione | Revolut | Altro |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Società Agricola \| Revolut \| \|', r'| \1 | €\2 | Società Agricola | Revolut | Altro (prodotti agricoli?) |'),
    (r'\| ([\d-]+) \| €([\d.]+) \| Liquida Snc Di \| Revolut \| \|', r'| \1 | €\2 | Liquida | Revolut | Altro (locale?) |'),
]

# Apply patterns
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Write back
with open('misc/transazioni_da_annotare.md', 'w', encoding='utf-8') as f:
    f.write(content)

# Count remaining empty notes
empty_notes = len(re.findall(r'\| Revolut \| \|$', content, re.MULTILINE))
empty_notes += len(re.findall(r'\| Illimity \| \|$', content, re.MULTILINE))

print(f"Pattern applicati con successo!")
print(f"Transazioni ancora da annotare: ~{empty_notes}")
