"""
Vaccine Knowledge Engine — breed-specific vaccine schedules, special health cases,
and age-based vaccination recommendations for dogs.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Core Vaccine Database
# ──────────────────────────────────────────────────────────────────────

CORE_VACCINES = {
    "DHPP (Distemper, Hepatitis, Parvovirus, Parainfluenza)": {
        "abbreviation": "DHPP",
        "type": "core",
        "puppy_schedule_weeks": [6, 10, 14, 18],
        "first_booster_months": 12,
        "booster_interval_years": 3,
        "description": "Protects against four serious viral diseases. Essential for all dogs.",
    },
    "Rabies": {
        "abbreviation": "Rabies",
        "type": "core",
        "puppy_schedule_weeks": [14],
        "first_booster_months": 12,
        "booster_interval_years": 3,
        "description": "Required by law in most regions. Protects against the fatal rabies virus.",
    },
}

NON_CORE_VACCINES = {
    "Bordetella (Kennel Cough)": {
        "abbreviation": "Bordetella",
        "type": "non-core",
        "puppy_schedule_weeks": [8],
        "first_booster_months": 12,
        "booster_interval_years": 1,
        "description": "Recommended for dogs that visit kennels, dog parks, or grooming facilities.",
        "recommended_for": ["all"],
    },
    "Leptospirosis": {
        "abbreviation": "Lepto",
        "type": "non-core",
        "puppy_schedule_weeks": [12, 16],
        "first_booster_months": 12,
        "booster_interval_years": 1,
        "description": "Protects against bacterial infection spread through water contaminated with animal urine.",
        "recommended_for": ["outdoor_dogs", "tropical_regions"],
    },
    "Lyme Disease": {
        "abbreviation": "Lyme",
        "type": "non-core",
        "puppy_schedule_weeks": [12, 16],
        "first_booster_months": 12,
        "booster_interval_years": 1,
        "description": "Recommended in tick-prone areas. Protects against Borrelia burgdorferi.",
        "recommended_for": ["tick_prone_areas"],
    },
    "Canine Influenza (H3N2/H3N8)": {
        "abbreviation": "CIV",
        "type": "non-core",
        "puppy_schedule_weeks": [8, 12],
        "first_booster_months": 12,
        "booster_interval_years": 1,
        "description": "Recommended for dogs in social settings (daycare, boarding, shows).",
        "recommended_for": ["social_dogs"],
    },
}


# ──────────────────────────────────────────────────────────────────────
# Breed-Specific Special Cases
# ──────────────────────────────────────────────────────────────────────

BREED_SPECIAL_CASES: Dict[str, Dict[str, Any]] = {
    "Pug": {
        "category": "brachycephalic",
        "warnings": [
            "🫁 **Brachycephalic breed** — monitor for breathing difficulties, especially in hot weather",
            "👁️ Prone to **eye injuries** (proptosis) due to shallow eye sockets",
            "🦴 Watch for **patellar luxation** and hip dysplasia",
            "🌡️ High risk of **heat stroke** — avoid strenuous exercise in warm weather",
        ],
        "vaccine_notes": "Brachycephalic dogs may have adverse reactions to anesthesia; inform your vet before any procedure.",
        "exercise_caution": "Limit intense exercise; short walks in cool weather preferred.",
    },
    "German Shepherd": {
        "category": "large_breed",
        "warnings": [
            "🦴 High risk of **hip and elbow dysplasia** — consider joint supplements early",
            "🫁 Prone to **degenerative myelopathy** in older age",
            "🩺 Watch for **exocrine pancreatic insufficiency (EPI)** — sudden weight loss, poor coat",
            "🐛 Susceptible to **bloat (GDV)** — feed smaller, frequent meals",
        ],
        "vaccine_notes": "German Shepherds may have a higher incidence of vaccine reactions. Monitor for 24 hours post-vaccination.",
        "exercise_caution": "High exercise needs but avoid excessive jumping in puppies under 18 months.",
    },
    "Golden Retriever": {
        "category": "large_breed",
        "warnings": [
            "🎗️ Higher risk of **cancer** (hemangiosarcoma, lymphoma) — regular vet screenings recommended",
            "🦴 Prone to **hip and elbow dysplasia**",
            "👂 Susceptible to **ear infections** due to floppy ears — clean ears regularly",
            "❤️ Watch for **subvalvular aortic stenosis** (heart condition)",
        ],
        "vaccine_notes": "Keep vaccinations up to date; Golden Retrievers in social settings benefit from Bordetella and CIV vaccines.",
        "exercise_caution": "Love swimming — excellent exercise, but dry ears thoroughly afterward.",
    },
    "Labrador Retriever": {
        "category": "large_breed",
        "warnings": [
            "🍖 Extremely prone to **obesity** — strict diet control essential",
            "🦴 High risk of **hip and elbow dysplasia**",
            "👂 Susceptible to **ear infections** — clean ears weekly",
            "🏊 Prone to **exercise-induced collapse (EIC)** in some lines",
        ],
        "vaccine_notes": "Labs are generally robust; standard vaccination schedule applies.",
        "exercise_caution": "High energy — needs 1-2 hours of exercise daily. Monitor weight closely.",
    },
    "Rottweiler": {
        "category": "large_breed",
        "warnings": [
            "🦴 High risk of **osteosarcoma** (bone cancer) — watch for persistent lameness",
            "🐛 Prone to **bloat (GDV)** — use slow-feed bowls, avoid exercise after meals",
            "❤️ Watch for **aortic stenosis** (heart condition)",
            "🦴 Susceptible to **hip dysplasia** and cruciate ligament injuries",
        ],
        "vaccine_notes": "Rottweilers may have a slightly increased risk of parvovirus — ensure timely puppy vaccinations.",
        "exercise_caution": "Moderate to high exercise needs. Avoid overexertion in hot weather.",
    },
    "Beagle": {
        "category": "medium_breed",
        "warnings": [
            "👂 Very prone to **ear infections** — floppy ears trap moisture",
            "🍖 Tendency to **obesity** — food-motivated breed, monitor portions",
            "🧬 Susceptible to **epilepsy** and **hypothyroidism**",
            "🦴 Watch for **intervertebral disc disease (IVDD)**",
        ],
        "vaccine_notes": "Standard vaccination schedule. Bordetella recommended due to social nature.",
        "exercise_caution": "Moderate exercise needs. Keep on leash — strong scent drive leads to wandering.",
    },
    "Dachshund": {
        "category": "small_breed",
        "warnings": [
            "🦴 **Very high risk of IVDD** (intervertebral disc disease) — avoid jumping, use ramps",
            "🍖 Prone to **obesity** which worsens spinal issues",
            "🦷 Susceptible to **dental disease** — regular dental care essential",
            "🩺 Watch for **patellar luxation**",
        ],
        "vaccine_notes": "Small breed — ensure proper dosing. Standard schedule applies.",
        "exercise_caution": "Moderate walks; absolutely avoid stairs and jumping on/off furniture.",
    },
    "Husky": {
        "category": "large_breed",
        "warnings": [
            "👁️ Prone to **cataracts** and **progressive retinal atrophy (PRA)**",
            "🌡️ **Heat sensitive** — not suited for tropical/hot climates without precautions",
            "🦴 Susceptible to **hip dysplasia**",
            "🧬 May carry **zinc deficiency** — watch for skin issues",
        ],
        "vaccine_notes": "Standard schedule. Extra parasite prevention in warmer climates.",
        "exercise_caution": "Extremely high energy — needs 2+ hours of vigorous exercise daily. Escape artists.",
    },
    "Shih Tzu": {
        "category": "brachycephalic",
        "warnings": [
            "🫁 **Brachycephalic breed** — breathing difficulties, especially in heat/humidity",
            "👁️ Prone to **eye problems** (keratitis, proptosis, dry eye)",
            "🦷 Susceptible to **dental overcrowding** and periodontal disease",
            "🩺 Watch for **patellar luxation** and **renal dysplasia**",
        ],
        "vaccine_notes": "Small brachycephalic breed — monitor closely after vaccinations for reactions.",
        "exercise_caution": "Low to moderate exercise. Avoid heat and humidity.",
    },
    "Border Collie": {
        "category": "medium_breed",
        "warnings": [
            "🧠 Extremely intelligent — **mental stimulation** is as important as physical exercise",
            "👁️ Prone to **Collie eye anomaly (CEA)** — genetic screening recommended",
            "🦴 Susceptible to **hip dysplasia** and **osteochondritis dissecans (OCD)**",
            "🧬 May carry **MDR1 gene mutation** — certain medications can be toxic",
        ],
        "vaccine_notes": "Standard schedule. Note MDR1 sensitivity — inform vet about breed.",
        "exercise_caution": "Highest exercise needs of any breed — needs 2+ hours of physical AND mental activity.",
    },
    "Cocker Spaniel": {
        "category": "medium_breed",
        "warnings": [
            "👂 Very prone to **chronic ear infections** — weekly ear cleaning essential",
            "👁️ Susceptible to **glaucoma** and **progressive retinal atrophy**",
            "🩺 Watch for **autoimmune hemolytic anemia (AIHA)**",
            "🍖 Tendency toward **obesity** — portion control needed",
        ],
        "vaccine_notes": "Standard schedule. Keep ears dry and clean post-vaccination.",
        "exercise_caution": "Moderate exercise needs. Thorough ear drying after swimming.",
    },
    "Srilankan Hound": {
        "category": "native_breed",
        "warnings": [
            "🌍 **Native breed** — generally hardier with fewer genetic health issues",
            "🐛 Higher risk of **tick-borne diseases** in tropical regions",
            "🦷 May be susceptible to **dental disease** if not maintained",
            "🩺 Watch for **skin parasites** (mange, ticks) common in tropical climates",
        ],
        "vaccine_notes": "Essential: Rabies (mandatory), DHPP, and Leptospirosis (tropical climate). Bordetella if socializing.",
        "exercise_caution": "Moderate to high exercise needs. Well-adapted to warm climates.",
    },
    "Malay Pointer": {
        "category": "native_breed",
        "warnings": [
            "🌍 **Native pointer breed** — generally robust and heat-tolerant",
            "🐛 Susceptible to **tropical parasites** — regular deworming essential",
            "🩺 Watch for **tick-borne diseases** (Ehrlichiosis, Babesiosis)",
            "🦴 Active breed — monitor for **joint wear** in older age",
        ],
        "vaccine_notes": "Core vaccines plus Leptospirosis strongly recommended for tropical environments.",
        "exercise_caution": "High energy working breed. Needs significant daily exercise.",
    },
    "Indie Native Dog": {
        "category": "native_breed",
        "warnings": [
            "🌍 **Indian native breed** — one of the healthiest dog types with minimal genetic issues",
            "🐛 Watch for **tick-borne diseases** and **skin infections** in humid climates",
            "🩺 Generally robust immune system, but still needs regular vaccinations",
            "🦷 Dental care important — may not receive regular professional cleaning",
        ],
        "vaccine_notes": "Core vaccines essential. Rabies mandatory. Leptospirosis recommended in monsoon regions.",
        "exercise_caution": "Moderate exercise needs. Highly adaptable to various climates.",
    },
}

# Default for breeds not explicitly listed
DEFAULT_SPECIAL_CASES = {
    "category": "general",
    "warnings": [
        "🩺 Regular veterinary check-ups every 6-12 months recommended",
        "🦷 Dental health is important — regular brushing and professional cleaning",
        "🐛 Keep up with parasite prevention (fleas, ticks, heartworm)",
        "🍖 Maintain a healthy weight with balanced nutrition",
    ],
    "vaccine_notes": "Follow standard vaccination schedule. Consult your vet for breed-specific recommendations.",
    "exercise_caution": "Adjust exercise to your dog's energy level and health status.",
}


class VaccineEngine:
    """Deterministic engine for dog vaccination schedules and breed-specific health knowledge."""

    @staticmethod
    def get_vaccine_schedule(breed: str, age_years: float, reference_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get the recommended vaccine schedule for a dog based on breed and age.

        Returns:
            Dict with 'overdue', 'upcoming', and 'completed_series' vaccine info.
        """
        if reference_date is None:
            reference_date = datetime.now(timezone.utc)

        age_weeks = age_years * 52
        age_months = age_years * 12
        result = {
            "breed": breed,
            "age_years": age_years,
            "age_months": round(age_months, 1),
            "overdue": [],
            "upcoming": [],
            "future": [],
            "notes": [],
        }

        all_vaccines = {**CORE_VACCINES, **NON_CORE_VACCINES}

        for vaccine_name, info in all_vaccines.items():
            abbrev = info["abbreviation"]
            vaccine_type = info["type"]

            # Check puppy series
            for week in info["puppy_schedule_weeks"]:
                if age_weeks < week:
                    # Not yet due
                    weeks_until = week - age_weeks
                    due_date = reference_date + timedelta(weeks=weeks_until)
                    result["future" if weeks_until > 4 else "upcoming"].append({
                        "vaccine": vaccine_name,
                        "abbreviation": abbrev,
                        "type": vaccine_type,
                        "series": f"Puppy dose (Week {week})",
                        "due_date": due_date.strftime("%Y-%m-%d"),
                        "weeks_until": round(weeks_until, 1),
                        "description": info["description"],
                    })
                elif age_weeks >= week and age_weeks < week + 4:
                    # Currently due
                    result["upcoming"].append({
                        "vaccine": vaccine_name,
                        "abbreviation": abbrev,
                        "type": vaccine_type,
                        "series": f"Puppy dose (Week {week}) — DUE NOW",
                        "due_date": reference_date.strftime("%Y-%m-%d"),
                        "weeks_until": 0,
                        "description": info["description"],
                        "urgent": True,
                    })

            # Check adult boosters
            if age_months >= info["first_booster_months"]:
                booster_interval_months = info["booster_interval_years"] * 12
                # Calculate when next booster would be due
                months_since_first = age_months - info["first_booster_months"]
                intervals_passed = months_since_first // booster_interval_months
                next_booster_month = info["first_booster_months"] + (intervals_passed + 1) * booster_interval_months
                months_until = next_booster_month - age_months

                if months_until <= 0:
                    result["overdue"].append({
                        "vaccine": vaccine_name,
                        "abbreviation": abbrev,
                        "type": vaccine_type,
                        "series": f"Booster (every {info['booster_interval_years']} year{'s' if info['booster_interval_years'] > 1 else ''})",
                        "description": info["description"],
                        "overdue_by_months": round(abs(months_until), 1),
                    })
                else:
                    due_date = reference_date + timedelta(days=months_until * 30.44)
                    target = "upcoming" if months_until <= 2 else "future"
                    result[target].append({
                        "vaccine": vaccine_name,
                        "abbreviation": abbrev,
                        "type": vaccine_type,
                        "series": f"Booster (every {info['booster_interval_years']} year{'s' if info['booster_interval_years'] > 1 else ''})",
                        "due_date": due_date.strftime("%Y-%m-%d"),
                        "months_until": round(months_until, 1),
                        "description": info["description"],
                    })

        # Add breed-specific notes
        breed_info = BREED_SPECIAL_CASES.get(breed, DEFAULT_SPECIAL_CASES)
        if breed_info.get("vaccine_notes"):
            result["notes"].append(breed_info["vaccine_notes"])

        # Sort by urgency
        result["overdue"].sort(key=lambda x: x.get("overdue_by_months", 0), reverse=True)
        result["upcoming"].sort(key=lambda x: x.get("weeks_until", x.get("months_until", 0)))

        return result

    @staticmethod
    def get_breed_special_cases(breed: str) -> Dict[str, Any]:
        """Get breed-specific health warnings and special considerations."""
        cases = BREED_SPECIAL_CASES.get(breed, DEFAULT_SPECIAL_CASES)
        return {
            "breed": breed,
            "category": cases["category"],
            "warnings": cases["warnings"],
            "vaccine_notes": cases.get("vaccine_notes", ""),
            "exercise_caution": cases.get("exercise_caution", ""),
        }

    @staticmethod
    def get_all_breeds() -> List[str]:
        """Get list of all breeds with special case data."""
        return list(BREED_SPECIAL_CASES.keys())

    @staticmethod
    def format_schedule_for_chat(schedule: Dict[str, Any]) -> str:
        """Format a vaccine schedule into a readable chat message."""
        lines = [f"## 💉 Vaccine Schedule for your {schedule['breed']} ({schedule['age_years']} years old)\n"]

        if schedule["overdue"]:
            lines.append("### 🚨 Overdue Vaccines")
            for v in schedule["overdue"]:
                lines.append(f"- **{v['abbreviation']}** — {v['series']} (overdue by ~{v['overdue_by_months']} months)")
            lines.append("")

        if schedule["upcoming"]:
            lines.append("### ⏰ Due Soon")
            for v in schedule["upcoming"]:
                urgent = " 🔴" if v.get("urgent") else ""
                lines.append(f"- **{v['abbreviation']}** — {v['series']}, due {v['due_date']}{urgent}")
            lines.append("")

        if schedule["future"]:
            lines.append("### 📋 Future Vaccines")
            for v in schedule["future"][:5]:  # Limit to next 5
                lines.append(f"- **{v['abbreviation']}** — {v['series']}, due {v['due_date']}")
            lines.append("")

        if schedule["notes"]:
            lines.append("### 📝 Breed-Specific Notes")
            for note in schedule["notes"]:
                lines.append(f"- {note}")

        return "\n".join(lines)
