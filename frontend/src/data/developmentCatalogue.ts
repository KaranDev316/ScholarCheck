import type { Scholarship } from './types'

/**
 * Development previews.
 *
 * These records restate the four S01 content fixtures as screens need them.
 * They are marked "Development preview" everywhere, carry no source-check
 * result, and are compiled out of production builds (see `catalogue.ts`).
 * Evidence numbering must stay stable: components and eligibility statements
 * point at it.
 */
export const developmentCatalogue: readonly Scholarship[] = [
  {
    id: 'cgsd-doctoral',
    title: 'Canada Graduate Research Scholarship – Doctoral (CGRS D)',
    provider: 'Government of Canada (CIHR, NSERC and SSHRC)',
    country: 'Canada',
    levels: ['PhD'],
    summary:
      'A federal doctoral award of CA$40,000 per year for 36 months, held while enrolled at an eligible Canadian institution. The programme description is a living-support award and does not mention tuition support.',
    tags: [],
    headline: {
      component: 'Living allowance',
      amount: 'CA$40,000',
      basis: 'per year for 36 months',
    },
    coverage: {
      tuition: {
        state: 'unspecified',
        detail: 'the award describes living support only',
      },
      livingCosts: { state: 'stated' },
      flights: { state: 'unspecified' },
    },
    components: [
      {
        id: 'cgsd-living-support',
        label: 'Living allowance',
        state: 'stated',
        amount: 'CA$40,000',
        basis: 'per year for 36 months',
        note: 'Paid to the award holder while the award is held.',
        conditions: ['Paid for 36 months.'],
        evidenceNumber: 1,
      },
      {
        id: 'cgsd-tuition',
        label: 'Tuition coverage',
        state: 'unspecified',
        note: 'The award description does not mention tuition support.',
      },
    ],
    eligibility: [
      {
        id: 'cgsd-doctoral-enrolment',
        statement:
          'Applicants who are not Canadian citizens, permanent residents or protected persons must be registered in a doctoral programme at an eligible Canadian institution by the application deadline.',
        state: 'stated',
        evidenceNumber: 2,
      },
      {
        id: 'cgsd-study-months',
        statement:
          'No more than 36 months of full-time equivalent doctoral study completed by 31 December of the calendar year of application.',
        state: 'stated',
        evidenceNumber: 3,
      },
    ],
    rounds: [
      {
        id: 'cgsd-direct-route',
        round: 'Direct to the agency',
        dateAsPublished: '17 October',
        status: 'Year not stated',
        note: 'The published page names a date but no year.',
      },
      {
        id: 'cgsd-institution-route',
        round: 'Through a Canadian institution',
        dateAsPublished: 'Set by the institution, often earlier',
        status: 'Not published',
        note: 'Contact the institution for its own deadline.',
      },
    ],
    application: {
      kind: 'confirm',
      note: 'No confirmed application route yet. Read the official requirements before acting.',
    },
    evidence: [
      {
        number: 1,
        claim: 'Published value and duration',
        passage: 'Value $40,000 per year Duration 36 months',
        url: 'https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 2,
        claim: 'Conditions for international applicants',
        passage:
          'If you are not a Canadian citizen, permanent resident of Canada or protected person under subsection 95(2) of the Immigration and Refugee Protection Act (Canada), you must be registered in your doctoral program of study at an eligible Canadian institution by the application deadline. Up to 15% of awards will be available to international applicants.',
        url: 'https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 3,
        claim: 'Study-duration limit for doctoral applicants',
        passage:
          'To be eligible to apply to the CGRS D program, you must have completed no more than 36 months of full-time equivalent study in the doctoral program, the PhD portion of the joint professional undergraduate/PhD program or the joint program for which you are requesting funding by December 31 of the calendar year of your application.',
        url: 'https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 4,
        claim: 'Published application deadline and routes',
        passage:
          'Application deadline Through a Canadian institution: Contact your institution (often significantly earlier than the agency’s deadline) Directly to the agency: October 17',
        url: 'https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp',
        savedAt: '2026-10-23T07:00:00Z',
      },
    ],
    links: {
      summary: 'https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp',
      requirements:
        'https://www.nserc-crsng.gc.ca/students-etudiants/pg-cs/cgsd-bescd_eng.asp#eligibility',
      portal: 'https://www.nserc-crsng.gc.ca/OnlineServices-ServicesEnLigne/index_eng.asp',
    },
    sourceCheck: null,
  },
  {
    id: 'udem-exemption-doctoral',
    title: 'Bourse d’exemption UdeM pour personnes étudiantes de l’international (3e cycle)',
    provider: 'Université de Montréal',
    country: 'Canada',
    levels: ['PhD'],
    summary:
      'A tuition exemption for international students admitted to a doctoral research programme at the Université de Montréal. It exempts the supplemental fees charged to international students, so the holder pays the Quebec doctoral rate. It is not a stipend.',
    tags: ['Awarded on admission'],
    headline: {
      component: 'Tuition exemption',
      amount: 'CA$24,067.80',
      basis: 'annual reduction at the 2026–2027 45-credit rate',
    },
    coverage: {
      tuition: {
        state: 'stated',
        detail: 'supplemental international tuition fees only, 2026–2027 rate',
      },
      livingCosts: {
        state: 'unspecified',
        detail: 'the exemption terms describe no living support',
      },
      flights: { state: 'unspecified' },
    },
    components: [
      {
        id: 'udem-tuition-exemption',
        label: 'Tuition exemption',
        state: 'stated',
        amount: 'CA$24,067.80',
        basis: 'per year, three full-time terms (45 credits), 2026–2027 rates',
        note: 'The holder pays the same tuition as Quebec doctoral students.',
        conditions: [
          'Calculated per credit and applied to the tuition invoice each term.',
          'Doctoral research programmes are eligible for 6 to 10 terms, depending on the programme’s normal full-time length.',
          'The value is set from the supplemental fees determined by the Quebec ministry.',
        ],
        evidenceNumber: 1,
      },
      {
        id: 'udem-living-support',
        label: 'Stipend or living allowance',
        state: 'unspecified',
        note: 'The exemption terms describe no living support.',
      },
    ],

    eligibility: [
      {
        id: 'udem-international-applicant',
        statement: 'Be an international student, other than a French or francophone Belgian student.',
        state: 'stated',
        evidenceNumber: 2,
      },
      {
        id: 'udem-admission-offer',
        statement:
          'Hold an offer of admission to a programme offered at the Université de Montréal.',
        state: 'stated',
        evidenceNumber: 2,
      },
      {
        id: 'udem-study-permits',
        statement:
          'Hold a valid Quebec Acceptance Certificate (CAQ) and study permit for every term of the programme.',
        state: 'stated',
        evidenceNumber: 2,
      },
      {
        id: 'udem-full-time-enrolment',
        statement: 'Be enrolled full-time, without interruption, for the whole programme.',
        state: 'stated',
        evidenceNumber: 2,
      },
      {
        id: 'udem-no-other-award',
        statement:
          'Not hold another tuition exemption granted by the Université de Montréal and not receive external funding from an organisation or third party.',
        state: 'stated',
        evidenceNumber: 2,
      },
    ],
    rounds: [
      {
        id: 'udem-2026-2027',
        round: '2026–2027 academic year',
        dateAsPublished: 'Not applicable',
        status: 'No separate application',
        note: 'Awarded with the admission offer.',
      },
    ],
    application: {
      kind: 'none',
      note: 'The source states no separate scholarship application. Apply for admission instead.',
    },

    evidence: [
      {
        number: 1,
        claim: 'Published exemption value for 2026–2027',
        passage:
          '[Table, transcribed, 3e cycle tab] Valeur de la bourse d’exemption UdeM — 534,84 $ par crédit; 8 022,60 $ par trimestre, statut temps plein (Équivalent 15 crédits); 24 067,80 $ par année (3 trimestres), statut temps plein (Équivalent 45 crédits). Année académique 2026-2027. Les montants indiqués ci-dessus sont en dollars canadiens.',
        url: 'https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 2,
        claim: 'Stated eligibility conditions',
        passage:
          "Vous pouvez obtenir la bourse d'exemption UdeM, si vous : êtes une personne étudiante de l'international (sauf personnes étudiantes françaises et belges francophones) avez reçu une offre d’admission dans un programme d'études offert à l'UdeM possédez des autorisations d'études valides (CAQ et permis d'études) pour l'ensemble des trimestres de votre programme d'études. êtes une personne étudiante inscrite à temps plein pour l'ensemble de votre programme d'études, et ce sans interruption (sauf absence autorisée) ne profitez pas déjà d'une autre forme d’exemption des droits de scolarité applicable par l'UdeM ne bénéficiez pas d'une source de financement externe de la part d'un organisme ou d'une tierce partie.",
        url: 'https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 3,
        claim: 'Award duration in terms',
        passage:
          "[Table, transcribed] Durée d'octroi de l'exemption — Programmes facturés au statut: Doctorat de recherche 6 à 10 (nombre de trimestres d'admissibilité, selon la durée normale de scolarité temps plein du programme d'études).",
        url: 'https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 4,
        claim: 'Exemption awarded without a separate application',
        passage:
          "Toutes les personnes étudiantes de l'international admises dans un programme de 3 e cycle de l'UdeM sont éligibles à la bourse d'exemption UdeM. Vous n'avez donc pas à faire de demande pour l'obtenir.",
        url: 'https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/',
        savedAt: '2026-10-23T07:00:00Z',
      },
    ],
    links: {
      summary: 'https://registraire.umontreal.ca/droits-de-scolarite/bourse-exemption/',
      requirements: 'https://esp.umontreal.ca/financement/',
      portal: 'https://admission.umontreal.ca/',
    },
    sourceCheck: null,
  },

  {
    id: 'rmit-research-stipend',
    title: 'RTP Stipend Scholarship (RSS) and RMIT Research Stipend Scholarship (RRSS)',
    provider: 'RMIT University and the Australian Government',
    country: 'Australia',
    levels: ['Research degree', 'PhD'],
    summary:
      'Research stipend awards for doctoral candidates at RMIT, awarded through a competitive round. International recipients also receive an international tuition-fee offset. Applications run in two stages.',
    tags: ['Two-stage application'],
    headline: {
      component: 'Research stipend',
      amount: 'A$36,245',
      basis: 'per year, published 2026 rate',
    },
    coverage: {
      tuition: {
        state: 'stated',
        detail: 'international tuition-fee offset awarded with the stipend',
      },
      livingCosts: { state: 'stated' },
      flights: { state: 'unspecified' },
    },
    components: [
      {
        id: 'rmit-stipend',
        label: 'Research stipend',
        state: 'stated',
        amount: 'A$36,245',
        basis: 'per year, pro rata for part-time study',
        conditions: [
          'The published amount is the 2026 rate; 2027 rates were not yet released.',
          'Amount is indexed annually.',
          'Paid for three and a half years for a doctoral programme.',
        ],
        evidenceNumber: 1,
      },
      {
        id: 'rmit-international-tuition-offset',
        label: 'International tuition-fee offset',
        state: 'stated',
        basis: 'for the duration of the stipend',
        note: 'An RTP International Tuition Fee Offset Scholarship (RIFOS) or RMIT Research International Tuition Fee Scholarship (RRITFS) is awarded with the stipend to international recipients.',
        conditions: ['Awarded to international recipients of the stipend.'],
        evidenceNumber: 2,
      },
      {
        id: 'rmit-relocation-allowance',
        label: 'Relocation allowance',
        state: 'stated',
        amount: 'Up to A$1,540',
        basis: 'one-off payment',
        conditions: ['Up to $515 per adult and $255 per child.', 'Maximum of $1,540.'],
        evidenceNumber: 3,
      },
    ],

    eligibility: [
      {
        id: 'rmit-hdr-enrolment',
        statement:
          'Be eligible to enrol, or currently be enrolled, in a higher degree by research programme at RMIT.',
        state: 'stated',
        evidenceNumber: 5,
      },
      {
        id: 'rmit-english-requirement',
        statement:
          'International applicants must meet the English language requirements by the application closing date.',
        state: 'stated',
        evidenceNumber: 6,
      },
      {
        id: 'rmit-supervisor-support',
        statement:
          'Provide evidence from an academic staff member who agrees to supervise the research when submitting the expression of interest.',
        state: 'stated',
        evidenceNumber: 7,
      },
      {
        id: 'rmit-no-earlier-doctorate',
        statement:
          'Applicants for a research doctorate must not already hold a research doctorate or an equivalent research qualification.',
        state: 'stated',
        evidenceNumber: 8,
      },
      {
        id: 'rmit-academic-priority',
        statement:
          'Priority is given to applicants with a high distinction (80% or higher) in the final two years of the qualifying programme.',
        state: 'stated',
        evidenceNumber: 9,
      },
    ],
    rounds: [
      {
        id: 'rmit-2027-international',
        round: '2027 scholarship round (international)',
        dateAsPublished: 'EOI 30 August 2026; full application 30 September 2026',
        status: 'Dates passed',
        note: 'The next round is not published. Not treated as closed.',
      },
    ],
    application: {
      kind: 'provider',
      note: 'Two stages: an expression of interest with a confirmed supervisor, then a full application.',
    },

    evidence: [
      {
        number: 1,
        claim: 'Published stipend rate',
        passage:
          'a stipend of $36,245 per annum pro rata (full-time study). This amount is subject to indexation annually',
        url: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 2,
        claim: 'International tuition-fee offset',
        passage:
          'international candidates in receipt of this scholarship are also awarded an RTP International Tuition Fee Offset Scholarship (RIFOS) or an RMIT Research International Tuition Fee Scholarship (RRITFS)',
        url: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 3,
        claim: 'Relocation allowance',
        passage:
          'a relocation allowance for the cost of relocating in order to take up their postgraduate research program. The amount is up to $515 per adult and $255 per child to a maximum of $1,540',
        url: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 4,
        claim: 'Scholarship duration',
        passage:
          'The standard duration of a research doctoral scholarship is three and a half years full-time.',
        url: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 5,
        claim: 'Enrolment eligibility',
        passage:
          '3.2. To meet the Commonwealth eligibility requirements, an applicant must be eligible to enrol, or currently be enrolled, in an HDR program at RMIT; and not be receiving any other Commonwealth award or scholarship designed to offset HDR tuition fees.',
        url: 'https://www.rmit.edu.au/research/research-degrees/terms-and-conditions',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 6,
        claim: 'English language requirement',
        passage:
          'International applicants must meet English language requirements by the application closing date to be considered for a scholarship.',
        url: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 7,
        claim: 'Supervisor support',
        passage:
          'All scholarship applicants must provide evidence from an academic member of staff who agrees to supervise your research when submitting an expression of interest.',
        url: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 8,
        claim: 'Prior research doctorate',
        passage:
          '3.3.4. If undertaking a research doctorate, a scholarship applicant must not hold a research doctorate or an equivalent research qualification unless they are an Australian and New Zealand citizen undertaking a second PhD in which case they are eligible for the RTP Fee Offset scholarship only.',
        url: 'https://www.rmit.edu.au/research/research-degrees/terms-and-conditions',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 9,
        claim: 'Academic priority',
        passage:
          'have achieved a high distinction in the final two years of the qualifying program(s). At RMIT, a grade of high distinction represents an academic achievement of 80% or higher',
        url: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 10,
        claim: 'Published 2027 round dates',
        passage:
          '[International column, transcribed] 2027 scholarship round opens for expressions of interest (EOIs): 1 June 2026. EOI deadline (last day to submit documents for EOI assessment): 30 August 2026. Full application deadline (last day to submit documents for full applications): 30 September 2026.',
        url: 'https://www.rmit.edu.au/research/research-degrees/scholarships',
        savedAt: '2026-10-23T07:00:00Z',
      },
    ],
    links: {
      summary: 'https://www.rmit.edu.au/scholarships/research/research-stipend',
      requirements: 'https://www.rmit.edu.au/research/research-degrees/terms-and-conditions',
      portal: 'https://www.rmit.edu.au/research/research-degrees/how-to-apply',
    },
    sourceCheck: null,
  },

  {
    id: 'usyd-rtp-stipend',
    title: 'Research Training Program (RTP) Stipend Scholarship',
    provider: 'Australian Government, administered by the University of Sydney',
    country: 'Australia',
    levels: ['Research degree', 'PhD'],
    summary:
      'A stipend for international and domestic higher-degree research students at the University of Sydney, awarded competitively. Holders are also awarded an RTP Fee Offset covering tuition for up to 14 research periods.',
    tags: ['Competitively awarded'],
    headline: {
      component: 'Annual stipend',
      amount: 'A$44,293',
      basis: 'per year, published 2027 rate',
    },
    coverage: {
      tuition: { state: 'stated', detail: '100% of tuition fees for up to 14 research periods' },
      livingCosts: { state: 'stated' },
      flights: { state: 'unspecified' },
    },
    components: [
      {
        id: 'usyd-stipend',
        label: 'Annual stipend',
        state: 'stated',
        amount: 'A$44,293',
        basis: 'per year (2027 rate)',
        conditions: ['The 2026 rate was $42,754 per year.', 'Competitively awarded.'],
        evidenceNumber: 1,
      },
      {
        id: 'usyd-tuition-offset',
        label: 'Tuition fee offset',
        state: 'stated',
        basis: 'up to 14 research periods',
        note: 'The RTP Fee Offset is awarded automatically with the stipend and covers 100% of tuition fees.',
        conditions: ['Awarded automatically to RTP Stipend Scholarship holders.'],
        evidenceNumber: 2,
      },
      {
        id: 'usyd-relocation-allowance',
        label: 'Relocation and thesis allowance',
        state: 'unspecified',
        note: 'Listed as a benefit; amounts are not stated on the page.',
        evidenceNumber: 1,
      },
      {
        id: 'usyd-health-cover',
        label: 'Overseas Student Health Cover',
        state: 'unspecified',
        note: 'Listed with the RTP Fee Offset; the value is not stated on the page.',
        evidenceNumber: 2,
      },
    ],

    eligibility: [
      {
        id: 'usyd-hdr-enrolment',
        statement:
          'Be a commencing or enrolled domestic or international higher degree by research student.',
        state: 'stated',
        evidenceNumber: 3,
      },
      {
        id: 'usyd-academic-record',
        statement:
          'Have an outstanding record of academic achievement and previous research experience.',
        state: 'stated',
        evidenceNumber: 4,
      },
      {
        id: 'usyd-admission-application',
        statement:
          'Apply for admission and submit all required admission documentation by the published deadline.',
        state: 'stated',
        evidenceNumber: 5,
      },
      {
        id: 'usyd-scholarship-form',
        statement: 'Submit the scholarship application form by the published deadline.',
        state: 'stated',
        evidenceNumber: 6,
      },
    ],
    rounds: [
      {
        id: 'usyd-rp1-2-2027',
        round: 'Research Period 1 and 2, 2027',
        dateAsPublished: '11 September 2026',
        status: 'Date passed',
        note: 'Marks this round only.',
      },
      {
        id: 'usyd-rp3-4-2027',
        round: 'Research Period 3 and 4, 2027',
        dateAsPublished: '18 December 2026',
        status: 'Deadline published',
        note: 'Check the official page in case the date changes.',
      },
    ],
    application: {
      kind: 'provider',
      note: 'Apply for admission, then submit the scholarship application form.',
    },

    evidence: [
      {
        number: 1,
        claim: 'Published stipend rate',
        passage:
          '[Table, transcribed] RTP Stipend Scholarship — Domestic and international students; commencing or enrolled in a higher degree by research; competitively awarded; $44,293 p.a. stipend (2027 rate), $42,754 p.a. stipend (2026 rate); relocation and thesis allowance.',
        url: 'https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 2,
        claim: 'Tuition fee offset and health cover',
        passage:
          '[Table, transcribed] RTP Fee Offset — International students; those awarded with a RTP Stipend Scholarship will automatically be awarded this scholarship; 100% tuition fees for up to 14 research periods; Overseas Student Health Cover (OSHC).',
        url: 'https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 3,
        claim: 'Stated eligibility',
        passage:
          'You must be a commencing or enrolled domestic or international higher degree by research student.',
        url: 'https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 4,
        claim: 'Academic record requirement',
        passage:
          'You must have an outstanding record of academic achievement and previous research experience.',
        url: 'https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 5,
        claim: 'Admission application step',
        passage:
          "Apply for admission and submit all required documentation for admission to a higher degree by research through Sydney Courses by the deadlines outlined in the 'Application and award timeline' table – these differ for domestic students and international students",
        url: 'https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 6,
        claim: 'Scholarship form step',
        passage: 'Submit the scholarship application form by the deadlines.',
        url: 'https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html',
        savedAt: '2026-10-23T07:00:00Z',
      },
      {
        number: 7,
        claim: 'Published deadlines',
        passage:
          '[Table, transcribed] Research Period 1 and 2, 2027 — submission deadline 11 September 2026. Research Period 3 and 4, 2027 — submission deadline 18 December 2026.',
        url: 'https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html',
        savedAt: '2026-10-23T07:00:00Z',
      },
    ],
    links: {
      summary:
        'https://www.sydney.edu.au/scholarships/australian-government-research-training-program.html',
      requirements:
        'https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html',
      portal: 'https://sydneyuniversity.formstack.com/forms/rtpapp',
    },
    sourceCheck: null,
  },
]

