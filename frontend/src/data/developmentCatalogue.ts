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

