// BEECEPTOR MOCK API SCRIPT FOR UMOOR SEHHAT
// This script creates mock API endpoints for testing data fetching
// Total: 500 Users, 100 Moze, 100 Doctors, 100 Students, 100 Patients, etc.

// Helper Functions
function generateITSId() {
    return Math.floor(10000000 + Math.random() * 90000000).toString();
}

function generatePhone() {
    return `+92-300-${Math.floor(1000000 + Math.random() * 9000000)}`;
}

function randomDate(start, end) {
    return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

function randomChoice(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

// Name pools
const maleNames = ['Ahmed', 'Ali', 'Hassan', 'Hussein', 'Mohammad', 'Omar', 'Yusuf', 'Ibrahim', 'Ismail', 'Mustafa'];
const femaleNames = ['Fatima', 'Aisha', 'Khadija', 'Maryam', 'Zainab', 'Hafsa', 'Ruqayyah', 'Umm Kulthum', 'Sakina', 'Zahra'];
const lastNames = ['Khan', 'Ali', 'Ahmed', 'Shah', 'Malik', 'Sheikh', 'Qureshi', 'Siddiqui', 'Ansari', 'Hashmi'];
const cities = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar', 'Quetta', 'Sialkot', 'Gujranwala'];

// =============================================================================
// 1. USERS ENDPOINT - 500 Users (Base for all other data)
// =============================================================================
mock.get('/api/users/', () => {
    const users = [];
    let userIdCounter = 1;
    
    // Create 500 users with proper role distribution
    const roles = [
        // Admins (10)
        ...Array(10).fill('badri_mahal_admin'),
        // Aamils (100) - one per Moze
        ...Array(100).fill('aamil'),
        // Moze Coordinators (100) - one per Moze
        ...Array(100).fill('moze_coordinator'),
        // Doctors (100)
        ...Array(100).fill('doctor'),
        // Students (100)
        ...Array(100).fill('student'),
        // Regular users and others (90)
        ...Array(90).fill('user')
    ];
    
    roles.forEach((role, index) => {
        const isAdmin = role === 'badri_mahal_admin';
        const gender = Math.random() > 0.5 ? 'male' : 'female';
        const firstName = gender === 'male' ? randomChoice(maleNames) : randomChoice(femaleNames);
        const lastName = randomChoice(lastNames);
        
        users.push({
            id: userIdCounter++,
            username: `${role}_${String(index + 1).padStart(3, '0')}`,
            email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@test.com`,
            first_name: firstName,
            last_name: lastName,
            role: role,
            its_id: generateITSId(),
            phone_number: generatePhone(),
            is_active: true,
            is_staff: isAdmin,
            is_superuser: isAdmin,
            date_joined: randomDate(new Date(2020, 0, 1), new Date()).toISOString(),
            gender: gender,
            city: randomChoice(cities)
        });
    });
    
    return {
        status: 200,
        body: {
            count: users.length,
            results: users
        }
    };
});

// =============================================================================
// 2. MOZE ENDPOINTS - 100 Moze Centers
// =============================================================================
mock.get('/api/moze/', () => {
    const mozeList = [];
    const mozeNames = [
        'Karachi Central', 'Lahore North', 'Islamabad Main', 'Rawalpindi East', 'Faisalabad West',
        'Multan South', 'Peshawar Central', 'Quetta Main', 'Sialkot North', 'Gujranwala East'
    ];
    
    for (let i = 1; i <= 100; i++) {
        const baseName = randomChoice(mozeNames);
        mozeList.push({
            id: i,
            name: `${baseName} Moze ${i}`,
            location: `${randomChoice(cities)}, Pakistan`,
            address: `Street ${i}, Block ${String.fromCharCode(65 + (i % 26))}, ${randomChoice(cities)}`,
            aamil_id: i, // Each Moze has one Aamil (user IDs 11-110)
            moze_coordinator_id: i + 100, // Coordinators (user IDs 111-210)
            contact_phone: generatePhone(),
            contact_email: `moze${i}@umoor.com`,
            established_date: randomDate(new Date(2010, 0, 1), new Date(2020, 0, 1)).toISOString().split('T')[0],
            is_active: true,
            capacity: Math.floor(50 + Math.random() * 200),
            created_at: randomDate(new Date(2020, 0, 1), new Date()).toISOString(),
            updated_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: mozeList.length,
            results: mozeList
        }
    };
});

// =============================================================================
// 3. STUDENTS ENDPOINTS - 100 Students
// =============================================================================
mock.get('/api/students/', () => {
    const students = [];
    const academicLevels = ['undergraduate', 'postgraduate', 'doctoral', 'diploma'];
    const enrollmentStatuses = ['active', 'suspended', 'graduated', 'withdrawn'];
    
    for (let i = 1; i <= 100; i++) {
        students.push({
            id: i,
            user_id: i + 210, // Student users (IDs 211-310)
            student_id: `STD${String(i).padStart(6, '0')}`,
            academic_level: randomChoice(academicLevels),
            enrollment_status: randomChoice(enrollmentStatuses),
            enrollment_date: randomDate(new Date(2020, 0, 1), new Date()).toISOString().split('T')[0],
            expected_graduation: randomDate(new Date(2024, 0, 1), new Date(2028, 0, 1)).toISOString().split('T')[0],
            gpa: (Math.random() * 3 + 1).toFixed(2),
            current_semester: Math.floor(1 + Math.random() * 8),
            moze_id: Math.floor(1 + Math.random() * 100)
        });
    }
    
    return {
        status: 200,
        body: {
            count: students.length,
            results: students
        }
    };
});

// =============================================================================
// 4. COURSES ENDPOINTS
// =============================================================================
mock.get('/api/courses/', () => {
    const courses = [
        {id: 1, code: 'MATH101', name: 'Mathematics I', credits: 3, is_active: true},
        {id: 2, code: 'ENG101', name: 'English Literature', credits: 3, is_active: true},
        {id: 3, code: 'SCI101', name: 'General Science', credits: 4, is_active: true},
        {id: 4, code: 'HIST101', name: 'Islamic History', credits: 2, is_active: true},
        {id: 5, code: 'ARAB101', name: 'Arabic Language', credits: 3, is_active: true},
        {id: 6, code: 'PHY101', name: 'Physics I', credits: 4, is_active: true},
        {id: 7, code: 'CHEM101', name: 'Chemistry I', credits: 4, is_active: true},
        {id: 8, code: 'BIO101', name: 'Biology I', credits: 4, is_active: true},
        {id: 9, code: 'COMP101', name: 'Computer Science', credits: 3, is_active: true},
        {id: 10, code: 'ECON101', name: 'Economics', credits: 3, is_active: true}
    ];
    
    return {
        status: 200,
        body: {
            count: courses.length,
            results: courses
        }
    };
});

// =============================================================================
// 5. DOCTORS ENDPOINTS - 100 Doctors
// =============================================================================
mock.get('/api/doctors/', () => {
    const doctors = [];
    const specialties = [
        'General Medicine', 'Cardiology', 'Pediatrics', 'Orthopedics', 'Dermatology',
        'Neurology', 'Gastroenterology', 'Oncology', 'Psychiatry', 'Ophthalmology'
    ];
    const qualifications = ['MBBS', 'MBBS, MD', 'MBBS, FCPS', 'MBBS, FRCS', 'MBBS, PhD'];
    
    for (let i = 1; i <= 100; i++) {
        doctors.push({
            id: i,
            user_id: i + 310, // Doctor users (IDs 311-410)
            name: `Dr. ${randomChoice(maleNames)} ${randomChoice(lastNames)}`,
            its_id: generateITSId(),
            specialty: randomChoice(specialties),
            qualification: randomChoice(qualifications),
            experience_years: Math.floor(1 + Math.random() * 25),
            license_number: `DOC${String(i).padStart(6, '0')}`,
            consultation_fee: Math.floor(500 + Math.random() * 2000),
            assigned_moze_id: Math.floor(1 + Math.random() * 100),
            is_verified: Math.random() > 0.1,
            is_available: Math.random() > 0.2,
            phone: generatePhone(),
            email: `doctor${i}@umoor.com`,
            languages_spoken: 'Urdu, English, Arabic',
            created_at: randomDate(new Date(2020, 0, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: doctors.length,
            results: doctors
        }
    };
});

// =============================================================================
// 6. PATIENTS & MEDICAL RECORDS ENDPOINTS - 100 Patients + 100 Records
// =============================================================================
mock.get('/api/patients/', () => {
    const patients = [];
    const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'];
    
    for (let i = 1; i <= 100; i++) {
        const gender = Math.random() > 0.5 ? 'male' : 'female';
        const firstName = gender === 'male' ? randomChoice(maleNames) : randomChoice(femaleNames);
        
        patients.push({
            id: i,
            its_id: generateITSId(),
            first_name: firstName,
            last_name: randomChoice(lastNames),
            arabic_name: `${firstName} ${randomChoice(lastNames)}`,
            date_of_birth: randomDate(new Date(1950, 0, 1), new Date(2010, 0, 1)).toISOString().split('T')[0],
            gender: gender,
            phone_number: generatePhone(),
            email: `patient${i}@test.com`,
            address: `House ${i}, ${randomChoice(cities)}, Pakistan`,
            emergency_contact_name: randomChoice(maleNames) + ' ' + randomChoice(lastNames),
            emergency_contact_phone: generatePhone(),
            emergency_contact_relationship: randomChoice(['Father', 'Mother', 'Spouse', 'Brother', 'Sister']),
            blood_group: randomChoice(bloodGroups),
            allergies: Math.random() > 0.7 ? 'Penicillin, Dust' : '',
            chronic_conditions: Math.random() > 0.8 ? 'Diabetes, Hypertension' : '',
            created_at: randomDate(new Date(2020, 0, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: patients.length,
            results: patients
        }
    };
});

mock.get('/api/medical-records/', () => {
    const records = [];
    const diagnoses = [
        'Hypertension', 'Diabetes Type 2', 'Common Cold', 'Migraine', 'Gastritis',
        'Asthma', 'Arthritis', 'Anxiety Disorder', 'Back Pain', 'Allergic Rhinitis'
    ];
    const treatments = [
        'Medication prescribed', 'Rest and fluids', 'Physical therapy', 'Dietary changes',
        'Follow-up in 2 weeks', 'Surgery recommended', 'Lifestyle modifications'
    ];
    
    for (let i = 1; i <= 100; i++) {
        records.push({
            id: i,
            patient_id: i,
            doctor_id: Math.floor(1 + Math.random() * 100),
            visit_date: randomDate(new Date(2023, 0, 1), new Date()).toISOString().split('T')[0],
            diagnosis: randomChoice(diagnoses),
            symptoms: 'Patient complaints of general discomfort',
            treatment_plan: randomChoice(treatments),
            medications: 'Paracetamol 500mg, Ibuprofen 400mg',
            notes: 'Patient responded well to treatment',
            follow_up_date: randomDate(new Date(), new Date(2024, 11, 31)).toISOString().split('T')[0],
            created_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: records.length,
            results: records
        }
    };
});

// =============================================================================
// 7. APPOINTMENTS ENDPOINTS - 100 Appointments
// =============================================================================
mock.get('/api/appointments/', () => {
    const appointments = [];
    const statuses = ['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'];
    const appointmentTypes = ['consultation', 'follow_up', 'emergency', 'routine_checkup'];
    
    for (let i = 1; i <= 100; i++) {
        const appointmentDate = randomDate(new Date(2024, 0, 1), new Date(2024, 11, 31));
        
        appointments.push({
            id: i,
            patient_id: i,
            doctor_id: Math.floor(1 + Math.random() * 100),
            appointment_date: appointmentDate.toISOString().split('T')[0],
            appointment_time: `${Math.floor(9 + Math.random() * 8)}:${randomChoice(['00', '30'])}`,
            status: randomChoice(statuses),
            appointment_type: randomChoice(appointmentTypes),
            reason: 'General consultation and health checkup',
            notes: 'Patient appears healthy, routine checkup completed',
            created_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString(),
            updated_at: randomDate(new Date(2023, 6, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: appointments.length,
            results: appointments
        }
    };
});

// =============================================================================
// 8. HOSPITALS ENDPOINTS
// =============================================================================
mock.get('/api/hospitals/', () => {
    const hospitals = [
        {
            id: 1,
            name: 'Saifee Hospital Mumbai',
            description: 'Premier healthcare facility in Mumbai',
            address: 'Charni Road, Mumbai, India',
            phone: '+91-22-67568000',
            email: 'info@saifeehospital.org',
            hospital_type: 'general',
            total_beds: 200,
            available_beds: 45,
            emergency_beds: 20,
            icu_beds: 15,
            is_active: true,
            is_emergency_capable: true,
            has_pharmacy: true,
            has_laboratory: true
        },
        {
            id: 2,
            name: 'Burhani Hospital Mumbai',
            description: 'Specialized medical care center',
            address: 'Mazgaon, Mumbai, India',
            phone: '+91-22-23750000',
            email: 'info@burhanihospital.org',
            hospital_type: 'specialty',
            total_beds: 150,
            available_beds: 30,
            emergency_beds: 15,
            icu_beds: 10,
            is_active: true,
            is_emergency_capable: true,
            has_pharmacy: true,
            has_laboratory: true
        },
        {
            id: 3,
            name: 'Karachi Saifee Hospital',
            description: 'Leading healthcare provider in Karachi',
            address: 'Saddar, Karachi, Pakistan',
            phone: '+92-21-35862000',
            email: 'info@karachisaifee.org',
            hospital_type: 'general',
            total_beds: 300,
            available_beds: 60,
            emergency_beds: 25,
            icu_beds: 20,
            is_active: true,
            is_emergency_capable: true,
            has_pharmacy: true,
            has_laboratory: true
        }
    ];
    
    return {
        status: 200,
        body: {
            count: hospitals.length,
            results: hospitals
        }
    };
});

// =============================================================================
// 9. SURVEYS ENDPOINTS - 10 Survey Forms
// =============================================================================
mock.get('/api/surveys/', () => {
    const surveys = [];
    const surveyTitles = [
        'Community Health Assessment', 'Education Quality Survey', 'Service Satisfaction Survey',
        'Healthcare Access Survey', 'Moze Services Evaluation', 'Youth Engagement Survey',
        'Digital Services Feedback', 'Annual Community Survey', 'Infrastructure Assessment',
        'Social Services Survey'
    ];
    
    for (let i = 1; i <= 10; i++) {
        surveys.push({
            id: i,
            title: surveyTitles[i - 1],
            description: `Comprehensive survey to assess ${surveyTitles[i - 1].toLowerCase()}`,
            created_by_id: Math.floor(1 + Math.random() * 10), // Admin users
            is_active: true,
            start_date: randomDate(new Date(2024, 0, 1), new Date()).toISOString().split('T')[0],
            end_date: randomDate(new Date(), new Date(2024, 11, 31)).toISOString().split('T')[0],
            max_responses: Math.floor(100 + Math.random() * 400),
            is_anonymous: Math.random() > 0.3,
            created_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: surveys.length,
            results: surveys
        }
    };
});

// =============================================================================
// 10. EVALUATION FORMS ENDPOINTS - 10 Evaluation Forms
// =============================================================================
mock.get('/api/evaluation-forms/', () => {
    const evaluationForms = [];
    const formTitles = [
        'Moze Performance Evaluation', 'Leadership Assessment', 'Service Quality Evaluation',
        'Team Performance Review', 'Annual Evaluation Form', 'Skill Assessment Form',
        'Community Impact Evaluation', 'Efficiency Evaluation', 'Quality Assurance Form',
        'Comprehensive Performance Review'
    ];
    
    for (let i = 1; i <= 10; i++) {
        evaluationForms.push({
            id: i,
            title: formTitles[i - 1],
            description: `Detailed evaluation form for ${formTitles[i - 1].toLowerCase()}`,
            target_role: randomChoice(['aamil', 'moze_coordinator', 'all']),
            created_by_id: Math.floor(1 + Math.random() * 10), // Admin users
            is_active: true,
            max_score: Math.floor(50 + Math.random() * 50),
            passing_score: Math.floor(30 + Math.random() * 20),
            time_limit_minutes: Math.floor(30 + Math.random() * 60),
            created_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString(),
            updated_at: randomDate(new Date(2023, 6, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: evaluationForms.length,
            results: evaluationForms
        }
    };
});

// =============================================================================
// 11. ARAZ (PETITIONS) ENDPOINTS - 100 Petitions
// =============================================================================
mock.get('/api/araz/', () => {
    const petitions = [];
    const categories = [
        'Academic Issues', 'Administrative Issues', 'Infrastructure', 'Health Services',
        'General Complaints', 'Financial Issues', 'Technical Support', 'Community Services'
    ];
    const statuses = ['pending', 'under_review', 'approved', 'rejected', 'closed'];
    const priorities = ['low', 'medium', 'high', 'urgent'];
    
    const petitionTitles = [
        'Request for library extension hours', 'Improvement in cafeteria services',
        'Additional parking space needed', 'Medical facility enhancement',
        'Internet connectivity issues', 'Air conditioning repair request',
        'Security system upgrade', 'Playground maintenance request',
        'Computer lab equipment update', 'Cleaning services improvement'
    ];
    
    for (let i = 1; i <= 100; i++) {
        const baseTitle = randomChoice(petitionTitles);
        
        petitions.push({
            id: i,
            title: `${baseTitle} - Request #${i}`,
            description: `Detailed description for ${baseTitle.toLowerCase()}. This petition addresses important community needs and requires prompt attention.`,
            category: randomChoice(categories),
            status: randomChoice(statuses),
            priority: randomChoice(priorities),
            created_by_id: Math.floor(11 + Math.random() * 400), // Various users
            assigned_to_id: Math.floor(1 + Math.random() * 10), // Admin users
            moze_id: Math.floor(1 + Math.random() * 100),
            expected_resolution_date: randomDate(new Date(), new Date(2024, 11, 31)).toISOString().split('T')[0],
            actual_resolution_date: Math.random() > 0.6 ? randomDate(new Date(2023, 0, 1), new Date()).toISOString().split('T')[0] : null,
            created_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString(),
            updated_at: randomDate(new Date(2023, 6, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: petitions.length,
            results: petitions
        }
    };
});

// =============================================================================
// 12. PHOTO ALBUMS ENDPOINTS
// =============================================================================
mock.get('/api/photo-albums/', () => {
    const albums = [];
    const albumTitles = [
        'Community Events 2024', 'Educational Programs', 'Health Camps', 'Cultural Programs',
        'Religious Gatherings', 'Youth Activities', 'Medical Camps', 'Social Services',
        'Infrastructure Projects', 'Volunteer Activities'
    ];
    
    for (let i = 1; i <= 10; i++) {
        albums.push({
            id: i,
            name: albumTitles[i - 1],
            description: `Photo collection from ${albumTitles[i - 1].toLowerCase()}`,
            moze_id: Math.floor(1 + Math.random() * 100),
            created_by_id: Math.floor(1 + Math.random() * 10),
            is_public: Math.random() > 0.3,
            allow_uploads: Math.random() > 0.4,
            event_date: randomDate(new Date(2023, 0, 1), new Date()).toISOString().split('T')[0],
            photo_count: Math.floor(5 + Math.random() * 25),
            created_at: randomDate(new Date(2023, 0, 1), new Date()).toISOString()
        });
    }
    
    return {
        status: 200,
        body: {
            count: albums.length,
            results: albums
        }
    };
});

// =============================================================================
// SUMMARY ENDPOINT
// =============================================================================
mock.get('/api/summary/', () => {
    return {
        status: 200,
        body: {
            message: "Umoor Sehhat Mock API - All Endpoints Active",
            total_data: {
                users: 500,
                moze_centers: 100,
                students: 100,
                doctors: 100,
                patients: 100,
                medical_records: 100,
                appointments: 100,
                hospitals: 3,
                surveys: 10,
                evaluation_forms: 10,
                petitions: 100,
                photo_albums: 10
            },
            endpoints: [
                '/api/users/', '/api/moze/', '/api/students/', '/api/courses/',
                '/api/doctors/', '/api/patients/', '/api/medical-records/',
                '/api/appointments/', '/api/hospitals/', '/api/surveys/',
                '/api/evaluation-forms/', '/api/araz/', '/api/photo-albums/'
            ]
        }
    };
});

console.log("🏥 Umoor Sehhat Mock API Initialized");
console.log("📊 Data Summary:");
console.log("- 500 Users (10 Admins, 100 Aamils, 100 Coordinators, 100 Doctors, 100 Students, 90 Others)");
console.log("- 100 Moze Centers");
console.log("- 100 Students with academic data");
console.log("- 100 Doctors with specializations");
console.log("- 100 Patients with 100 medical records");
console.log("- 100 Appointments (patient-doctor pairs)");
console.log("- 3 Major hospitals");
console.log("- 10 Survey forms");
console.log("- 10 Evaluation forms");
console.log("- 100 Araz petitions");
console.log("- 10 Photo albums");
console.log("✅ All 9 Django apps covered!");