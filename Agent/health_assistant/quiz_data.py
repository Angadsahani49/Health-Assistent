"""
Quiz Data for the Health Awareness Assistant.
Contains educational multiple-choice questions with answer choices, correct answers,
categories, and detailed explanations to reinforce preventive health literacy.
"""

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "category": "Physical Activity",
        "question": "According to the World Health Organization (WHO), how much moderate-intensity aerobic physical activity is recommended weekly for adults (18–64 years)?",
        "options": [
            "At least 45 minutes per week",
            "At least 150 to 300 minutes per week",
            "Exactly 60 minutes every single day without rest",
            "At least 600 minutes per week"
        ],
        "answer_index": 1,
        "explanation": "The WHO recommends that adults undertake at least 150–300 minutes of moderate-intensity physical activity (such as brisk walking, cycling, or swimming), or at least 75–150 minutes of vigorous-intensity aerobic physical activity throughout the week for substantial health benefits."
    },
    {
        "id": 2,
        "category": "Sleep Health",
        "question": "What is the recommended average duration of quality sleep per night for healthy adults according to the National Sleep Foundation?",
        "options": [
            "4 to 5 hours",
            "5 to 6 hours",
            "7 to 9 hours",
            "10 to 12 hours"
        ],
        "answer_index": 2,
        "explanation": "Healthy adults typically require 7 to 9 hours of restorative sleep each night. Consistent sleep deprivation is linked with impaired immune function, metabolic disturbances, cardiovascular strain, and decreased cognitive alertness."
    },
    {
        "id": 3,
        "category": "Hydration",
        "question": "Which of the following is one of the most reliable and immediate indicators of adequate daily hydration in healthy individuals?",
        "options": [
            "Drinking only when feeling intensely thirsty",
            "Light straw or pale yellow urine color",
            "Consuming energy drinks before meals",
            "Dark amber colored urine"
        ],
        "answer_index": 1,
        "explanation": "Urine color is a simple, practical indicator of hydration status. Light, pale straw-colored urine usually signifies optimal hydration. Dark amber urine indicates concentrated urine and a need for greater fluid intake. Relying solely on thirst can be deceptive as thirst often manifests after mild dehydration has already set in."
    },
    {
        "id": 4,
        "category": "Medication & Antibiotic Awareness",
        "question": "Why are antibiotics ineffective against illnesses like the common cold, seasonal influenza (flu), or COVID-19?",
        "options": [
            "Antibiotics only work if taken with citrus fruits",
            "Cold and flu viruses mutate into bacteria inside the body",
            "These illnesses are caused by viruses, whereas antibiotics only kill or inhibit bacteria",
            "Antibiotics expire immediately upon contact with saliva"
        ],
        "answer_index": 2,
        "explanation": "Antibiotics target specific bacterial structures and biological pathways; they have zero effect against viruses. Using antibiotics for viral infections does not cure the illness, can cause unnecessary side effects, and accelerates global antibiotic resistance."
    },
    {
        "id": 5,
        "category": "Cardiovascular Health",
        "question": "In general health guidelines, what is considered a normal resting blood pressure range for healthy adults?",
        "options": [
            "Systolic less than 120 mm Hg and Diastolic less than 80 mm Hg",
            "Systolic 140–159 mm Hg and Diastolic 90–99 mm Hg",
            "Systolic above 160 mm Hg regardless of Diastolic",
            "Systolic exactly equal to heart rate"
        ],
        "answer_index": 0,
        "explanation": "According to major cardiology associations (including AHA and ACC), normal blood pressure for healthy adults is generally defined as systolic pressure under 120 mm Hg and diastolic pressure under 80 mm Hg (<120/<80 mm Hg). Elevated readings warrant routine clinical consultation."
    },
    {
        "id": 6,
        "category": "Nutrition & Digestion",
        "question": "What is the primary physiological benefit of consuming adequate dietary fiber from whole grains, legumes, vegetables, and fruits?",
        "options": [
            "It eliminates the need to drink water",
            "It supports gut microbiota, regulates bowel movements, and aids blood sugar and cholesterol control",
            "It acts as a synthetic antibiotic in the stomach",
            "It instantly burns body fat without physical exercise"
        ],
        "answer_index": 1,
        "explanation": "Dietary fiber (both soluble and insoluble) normalizes bowel movements, feeds beneficial gut bacteria, blunts rapid glucose spikes after meals, and assists in lowering LDL ('bad') cholesterol levels."
    },
    {
        "id": 7,
        "category": "Preventive Care & Skin Health",
        "question": "When applying broad-spectrum sunscreen for everyday ultraviolet (UV) protection during outdoor activities, what is the minimum recommended Sun Protection Factor (SPF)?",
        "options": [
            "SPF 4",
            "SPF 8",
            "SPF 30",
            "SPF 100 is strictly the only effective option"
        ],
        "answer_index": 2,
        "explanation": "Dermatologists and cancer prevention organizations recommend a broad-spectrum sunscreen with an SPF of at least 30. Broad-spectrum SPF 30 blocks approximately 97% of UVB rays. Regular reapplication every two hours (or after swimming/sweating) is essential."
    },
    {
        "id": 8,
        "category": "Stress Management",
        "question": "How does intentional diaphragmatic breathing (deep 'belly breathing') physically help reduce acute psychological stress?",
        "options": [
            "It stimulates the sympathetic 'fight-or-flight' surge",
            "It activates the parasympathetic nervous system via the vagus nerve, slowing heart rate and inducing calmness",
            "It immediately halts all blood circulation to the brain",
            "It replaces the body's need for oxygen"
        ],
        "answer_index": 1,
        "explanation": "Slow, deep diaphragmatic breathing engages the vagus nerve and activates the parasympathetic nervous system—the body's natural 'rest-and-digest' mechanism. This down-regulates cortisol release, slows the heart rate, and lowers muscle tension."
    }
]
