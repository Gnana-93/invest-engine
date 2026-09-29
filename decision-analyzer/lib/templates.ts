import type { DecisionTemplate, Option, Scenario } from "./types";

export const arrangedMarriageTemplate: DecisionTemplate = {
  id: "arranged-marriage",
  title: "Should I proceed with arranged marriage now or wait?",
  description:
    "Analyze whether to start the arranged marriage process immediately, wait to work on readiness, or proceed with a slower timeline.",
  category: "Relationships",
  icon: "Heart",
  options: [
    {
      id: "proceed-now",
      name: "Proceed with arranged marriage now",
      description:
        "Start meeting matches immediately, aim to marry within 12-18 months",
      scenarios: [
        {
          id: "am-now-1",
          description: "Find great match quickly, have fulfilling marriage",
          probability: 25,
          value: 85,
          explanation:
            "Strong compatibility, mutual respect, family support, personal growth together. Everything aligns well and you build a happy life.",
        },
        {
          id: "am-now-2",
          description: "Find decent match, have good marriage",
          probability: 35,
          value: 60,
          explanation:
            "Solid partnership with mutual respect. Not perfect but satisfying. You grow to love each other and build a stable life together.",
        },
        {
          id: "am-now-3",
          description:
            "Suitable match, acceptable but not great marriage",
          probability: 20,
          value: 20,
          explanation:
            "Marriage is manageable but unfulfilling. Some compatibility issues. You wonder if waiting would have been better.",
        },
        {
          id: "am-now-4",
          description:
            "Marry wrong person due to pressure, unhappy marriage",
          probability: 15,
          value: -50,
          explanation:
            "Rushed decision leads to poor match. Constant conflict, incompatibility, regret. Feel trapped but stay due to social/family pressure.",
        },
        {
          id: "am-now-5",
          description:
            "No suitable match found in 1 year, continue searching",
          probability: 5,
          value: -10,
          explanation:
            "Meet several people but no strong connection. Time invested with no result. Family asking questions. Process continues.",
        },
      ],
    },
    {
      id: "wait-1-2-years",
      name: "Wait 1-2 years before starting",
      description:
        "Work on personal readiness, clarity, and maturity, then start the process",
      scenarios: [
        {
          id: "am-wait-1",
          description: "Work on readiness gaps, then find great match",
          probability: 30,
          value: 85,
          explanation:
            "Use time to gain clarity about what you want, improve emotional maturity, achieve career goals. Enter process more confident and make better choice.",
        },
        {
          id: "am-wait-2",
          description:
            "Feel more ready, find decent match and have good marriage",
          probability: 30,
          value: 60,
          explanation:
            "Even modest improvement in readiness helps. You approach the process more thoughtfully and find a good partner.",
        },
        {
          id: "am-wait-3",
          description:
            "Don't actually work on gaps, same situation later",
          probability: 15,
          value: -25,
          explanation:
            "Time passes but you don't use it productively. Still feel unready after 2 years. Parents frustrated. Wasted time.",
        },
        {
          id: "am-wait-4",
          description: "Family tension increases significantly",
          probability: 15,
          value: -30,
          explanation:
            "Parents become very upset about waiting. Constant pressure, guilt, strained relationships. Creates significant stress.",
        },
        {
          id: "am-wait-5",
          description:
            "Miss good matches, pool shrinks, harder to find later",
          probability: 10,
          value: -40,
          explanation:
            "Age becomes a factor. Some good matches marry others. Pool of available matches decreases. Process becomes harder.",
        },
      ],
    },
    {
      id: "proceed-slowly",
      name: "Proceed slowly (18-24 month timeline)",
      description:
        "Start meeting people but take time to assess, no rushing",
      scenarios: [
        {
          id: "am-slow-1",
          description:
            "Slow pace allows proper assessment, find great match",
          probability: 25,
          value: 80,
          explanation:
            "Extended timeline reduces pressure. You can evaluate compatibility thoroughly. Find someone great without rushing.",
        },
        {
          id: "am-slow-2",
          description:
            "Slow pace helps both assess fit, good marriage",
          probability: 35,
          value: 55,
          explanation:
            "Thoughtful approach leads to solid choice. Both families appreciate the careful consideration. Good outcome.",
        },
        {
          id: "am-slow-3",
          description:
            "Slow pace frustrates parents and potential matches",
          probability: 20,
          value: -20,
          explanation:
            "Some families and matches lose patience with slow timeline. Creates friction. Some good matches move on.",
        },
        {
          id: "am-slow-4",
          description:
            "Use slow pace as avoidance, no real progress",
          probability: 15,
          value: -25,
          explanation:
            "Slow timeline becomes indefinite delay. You're still not working on readiness. Just postponing decision.",
        },
        {
          id: "am-slow-5",
          description:
            "Lose good match because they find faster match",
          probability: 5,
          value: -30,
          explanation:
            "Meet someone promising but your slow pace causes them to accept another proposal. Missed opportunity due to indecision.",
        },
      ],
    },
    {
      id: "no-marriage",
      name: "No marriage (stay single by choice)",
      description:
        "Step away from the marriage process entirely and build life as a single person",
      scenarios: [
        {
          id: "am-single-1",
          description: "Thrive single: career, freedom, and peace of mind",
          probability: 30,
          value: 75,
          explanation:
            "You invest fully in career, health, friendships, and hobbies. Financial independence grows. Life feels full and self-directed. Pressure fades as you settle into your choice.",
        },
        {
          id: "am-single-2",
          description:
            "Content single life with occasional loneliness or social pressure",
          probability: 35,
          value: 35,
          explanation:
            "Mostly good: freedom, own space, own schedule. But weddings and family gatherings sting sometimes, and relatives keep asking. Manageable and worth it overall.",
        },
        {
          id: "am-single-3",
          description:
            "Loneliness and family pressure weigh heavily over time",
          probability: 20,
          value: -25,
          explanation:
            "Friends marry and drift away. Parents' disappointment doesn't ease. Loneliness hits in evenings, festivals, and illness. Doubt your choice in low phases.",
        },
        {
          id: "am-single-4",
          description:
            "No partner in health emergencies or old age, support gaps hurt",
          probability: 10,
          value: -45,
          explanation:
            "Hospital forms, emergencies, and aging parents expose the missing support structure. You lean on friends and paid help, but the gap is real and expensive.",
        },
        {
          id: "am-single-5",
          description:
            "Change of mind later, but good matches are gone",
          probability: 5,
          value: -35,
          explanation:
            "At 35+ you decide you do want a partner after all. The pool has shrunk and the process is harder now. Regret about closing the door early.",
        },
      ],
    },
  ],
};

export const careerTransitionTemplate: DecisionTemplate = {
  id: "career-transition",
  title: "Should I change careers now?",
  description:
    "Analyze whether to switch to a new career path immediately, prepare first, or stay in your current field.",
  category: "Career",
  icon: "Briefcase",
  options: [
    {
      id: "switch-now",
      name: "Switch careers immediately",
      description:
        "Make the career transition right now without delay",
      scenarios: [
        {
          id: "career-now-1",
          description:
            "New career is fulfilling, successful transition",
          probability: 30,
          value: 90,
          explanation:
            "You love the new work, income is good or better, clear career growth path, no regrets about switching. Best case scenario.",
        },
        {
          id: "career-now-2",
          description:
            "New career is good, modest improvement over current",
          probability: 35,
          value: 50,
          explanation:
            "Better than before and satisfying, though not amazing. Decent income, more fulfilling work. Glad you switched.",
        },
        {
          id: "career-now-3",
          description: "Struggle initially but eventually succeed",
          probability: 20,
          value: 30,
          explanation:
            "Difficult transition period with financial stress and learning curve. Takes 2-3 years to stabilize but eventually works out.",
        },
        {
          id: "career-now-4",
          description:
            "New career doesn't work out, regret switching",
          probability: 10,
          value: -60,
          explanation:
            "Wrong fit for your skills or interests. Income drops significantly. Wasted time and money. Deep regret about rushing.",
        },
        {
          id: "career-now-5",
          description:
            "Fail in new career, forced to return to old field",
          probability: 5,
          value: -80,
          explanation:
            "Major setback. Lost time, money, and confidence. Have to restart in old field at lower level. Significant career damage.",
        },
      ],
    },
    {
      id: "stay-current",
      name: "Stay in current career",
      description:
        "Continue in current field, focus on advancement and growth",
      scenarios: [
        {
          id: "career-stay-1",
          description:
            "Find renewed passion, advance in current field",
          probability: 25,
          value: 70,
          explanation:
            "Get promotion or better projects. Rediscover meaning in your work. Realize the grass isn't greener. Career flourishes.",
        },
        {
          id: "career-stay-2",
          description:
            "Career continues steadily, stable but not exciting",
          probability: 40,
          value: 20,
          explanation:
            "Safe and predictable path. Financial security but limited fulfillment. Some regret about not trying something new.",
        },
        {
          id: "career-stay-3",
          description:
            "Remain unfulfilled, growing regret about not switching",
          probability: 25,
          value: -30,
          explanation:
            'Years pass feeling stuck. Growing resentment and "what if" thoughts. Feel like you missed your chance.',
        },
        {
          id: "career-stay-4",
          description:
            "Industry declines, forced career change later anyway",
          probability: 10,
          value: -50,
          explanation:
            "Industry disruption or decline forces change when you're older. Much harder to switch. Fewer options. Worse position.",
        },
      ],
    },
    {
      id: "prepare-then-switch",
      name: "Prepare for 6-12 months, then switch",
      description:
        "Build skills, save money, make connections, then transition strategically",
      scenarios: [
        {
          id: "career-prep-1",
          description:
            "Preparation pays off, smooth successful transition",
          probability: 40,
          value: 85,
          explanation:
            "Skills ready, financial buffer built, network established. Confident switch with minimal stress. Excellent outcome.",
        },
        {
          id: "career-prep-2",
          description:
            "Preparation helps, good transition with manageable challenges",
          probability: 35,
          value: 60,
          explanation:
            "Better positioned than switching immediately. Some challenges but you handle them. Decent outcome, glad you prepared.",
        },
        {
          id: "career-prep-3",
          description:
            "Preparation period drags on, lose motivation",
          probability: 15,
          value: -20,
          explanation:
            'Never feel "ready enough." Preparation becomes procrastination. Never actually make the switch. Time wasted.',
        },
        {
          id: "career-prep-4",
          description:
            "Market changes during preparation, opportunity lost",
          probability: 10,
          value: -40,
          explanation:
            "Industry shifts, hiring freezes, or opportunity window closes while you prepare. Timing missed. Harder to switch later.",
        },
      ],
    },
  ],
};

export const buyingHouseTemplate: DecisionTemplate = {
  id: "buying-house",
  title: "Should I buy a house now?",
  description:
    "Analyze whether to purchase property now, wait to save more, or continue renting long-term.",
  category: "Finance",
  icon: "Home",
  options: [
    {
      id: "buy-now",
      name: "Buy a house now",
      description:
        "Purchase property at current market prices with current savings",
      scenarios: [
        {
          id: "house-buy-1",
          description: "Property value increases, excellent investment",
          probability: 30,
          value: 80,
          explanation:
            "Market appreciates 3-5% annually. Build significant equity. Financial security. Pride of ownership. Great decision.",
        },
        {
          id: "house-buy-2",
          description:
            "Property value stable, enjoy homeownership benefits",
          probability: 35,
          value: 50,
          explanation:
            "No major appreciation but no loss either. Stable housing costs. Building equity slowly. Pride of ownership. Decent outcome.",
        },
        {
          id: "house-buy-3",
          description: "Property value decreases slightly, some regret",
          probability: 20,
          value: -20,
          explanation:
            "Market softens, property worth less than purchase price. Underwater on mortgage. Wish you had waited. Manageable but frustrating.",
        },
        {
          id: "house-buy-4",
          description:
            "Job relocation required, forced to sell at loss",
          probability: 10,
          value: -60,
          explanation:
            "Career opportunity requires move. Must sell quickly. Market is down. Selling costs. Significant financial loss.",
        },
        {
          id: "house-buy-5",
          description: "Major market crash, significant loss",
          probability: 5,
          value: -80,
          explanation:
            "Deep recession, property value drops 20-30%. Deeply underwater. Financial stress. Major regret about timing.",
        },
      ],
    },
    {
      id: "wait-save-more",
      name: "Wait 1-2 years, save larger down payment",
      description:
        "Continue renting, build savings, buy with stronger financial position",
      scenarios: [
        {
          id: "house-wait-1",
          description:
            "Market cools, buy at better price with larger down payment",
          probability: 25,
          value: 85,
          explanation:
            "Patience pays off. Prices drop or stabilize. Your larger down payment means lower mortgage, better rate. Excellent outcome.",
        },
        {
          id: "house-wait-2",
          description:
            "Save more, buy similar house with less debt",
          probability: 30,
          value: 60,
          explanation:
            "Market stays similar but you have 20-30% down instead of 10%. Lower monthly payment. More comfortable financially.",
        },
        {
          id: "house-wait-3",
          description:
            "Market stays same, rent paid was opportunity cost",
          probability: 25,
          value: -10,
          explanation:
            "Prices don't change. Rent you paid could have been building equity. No real advantage from waiting. Time lost.",
        },
        {
          id: "house-wait-4",
          description:
            "Market increases significantly, priced out",
          probability: 15,
          value: -50,
          explanation:
            "Prices rise 10-20% while you save. Your savings can't keep up. Now need much more for down payment. Harder to buy.",
        },
        {
          id: "house-wait-5",
          description:
            "Interest rates increase, affordability decreases",
          probability: 5,
          value: -40,
          explanation:
            "Rates jump 2-3%. Monthly payment for same house is now much higher. Your savings are offset by higher rates.",
        },
      ],
    },
    {
      id: "continue-renting",
      name: "Continue renting indefinitely",
      description:
        "Invest savings in other assets, maintain flexibility, rent long-term",
      scenarios: [
        {
          id: "house-rent-1",
          description:
            "Investments outperform real estate, maintain flexibility",
          probability: 30,
          value: 70,
          explanation:
            "Stock/business investments return 8-12% vs 3-5% home appreciation. Can relocate easily. No maintenance hassles. Good outcome.",
        },
        {
          id: "house-rent-2",
          description:
            "Renting works well, enjoy flexibility and simplicity",
          probability: 35,
          value: 40,
          explanation:
            "Comfortable lifestyle, no regrets. Freedom to move. No maintenance stress. Building wealth other ways. Decent outcome.",
        },
        {
          id: "house-rent-3",
          description:
            "Rent increases significantly, financial strain",
          probability: 20,
          value: -30,
          explanation:
            "Rent goes up 5-8% annually. Housing costs consume more income. No equity building. Regret not locking in housing cost.",
        },
        {
          id: "house-rent-4",
          description:
            "Miss out on property appreciation, regret not buying",
          probability: 15,
          value: -60,
          explanation:
            "Friends who bought build significant wealth through appreciation. You paid similar in rent with nothing to show. Opportunity cost hurts.",
        },
      ],
    },
  ],
};

export const startingBusinessTemplate: DecisionTemplate = {
  id: "starting-business",
  title: "Should I start my own business?",
  description:
    "Analyze whether to start a business now, prepare while employed, or stay in stable employment.",
  category: "Entrepreneurship",
  icon: "Rocket",
  options: [
    {
      id: "start-now",
      name: "Start business immediately (full-time)",
      description:
        "Quit job and go all-in on your business idea right now",
      scenarios: [
        {
          id: "biz-now-1",
          description:
            "Business succeeds, financial freedom and fulfillment",
          probability: 15,
          value: 95,
          explanation:
            "Business grows profitably. Income exceeds job salary. Complete autonomy. Building significant wealth. Dream outcome.",
        },
        {
          id: "biz-now-2",
          description:
            "Business is moderately successful, decent income",
          probability: 20,
          value: 60,
          explanation:
            "Business sustains you with income similar to job. More fulfilling work. Some stress but manageable. Glad you tried.",
        },
        {
          id: "biz-now-3",
          description:
            "Business struggles, barely break even for 2-3 years",
          probability: 25,
          value: 10,
          explanation:
            "Extremely hard work with minimal financial reward. High stress. Depleting savings. Uncertain if it will work out.",
        },
        {
          id: "biz-now-4",
          description:
            "Business fails, return to employment with gap in resume",
          probability: 30,
          value: -60,
          explanation:
            "Business doesn't work. Savings depleted. 2-3 year gap makes job search harder. Financial stress. Regret rushing.",
        },
        {
          id: "biz-now-5",
          description:
            "Business fails catastrophically, significant debt",
          probability: 10,
          value: -90,
          explanation:
            "Major financial loss. Debt from business loans. Damaged credit. Years to recover. Severe regret about not preparing better.",
        },
      ],
    },
    {
      id: "stay-employed",
      name: "Stay in stable employment",
      description:
        "Continue current job, maintain financial security",
      scenarios: [
        {
          id: "biz-stay-1",
          description:
            "Advance in career, realize employment suits you better",
          probability: 30,
          value: 65,
          explanation:
            "Get promotion and interesting work. Realize stability and benefits are valuable. Glad you didn't risk it. Good outcome.",
        },
        {
          id: "biz-stay-2",
          description:
            'Stable career but always wonder "what if"',
          probability: 40,
          value: 15,
          explanation:
            "Financial security but nagging regret. Watch others start businesses. Wonder if you missed your chance. Unfulfilled.",
        },
        {
          id: "biz-stay-3",
          description:
            "Job becomes unfulfilling, deep regret about not trying",
          probability: 20,
          value: -40,
          explanation:
            "Years pass feeling stuck. Business idea was probably viable. Opportunity window closes. Deep regret about fear.",
        },
        {
          id: "biz-stay-4",
          description:
            "Layoff or industry disruption, wish you had built own thing",
          probability: 10,
          value: -50,
          explanation:
            "Job loss when older. Harder to start business now. Wish you had taken the chance when younger. Regret and uncertainty.",
        },
      ],
    },
    {
      id: "side-hustle",
      name: "Build business as side project (6-12 months)",
      description:
        "Keep job while validating business idea, transition when viable",
      scenarios: [
        {
          id: "biz-side-1",
          description:
            "Side business proves viable, smooth transition to full-time",
          probability: 35,
          value: 90,
          explanation:
            "Validate idea with customers while keeping income. Build runway. Confident transition. Best of both worlds. Excellent outcome.",
        },
        {
          id: "biz-side-2",
          description:
            "Side business grows steadily, eventually go full-time",
          probability: 30,
          value: 70,
          explanation:
            "Takes longer but less risky. Build business to replace 50% of income before quitting. Smart, measured approach. Good outcome.",
        },
        {
          id: "biz-side-3",
          description:
            "Side business shows idea isn't viable, pivot or abandon",
          probability: 20,
          value: 20,
          explanation:
            "Learn business won't work without major financial loss. Valuable learning. Keep job. Try different idea or stay employed.",
        },
        {
          id: "biz-side-4",
          description:
            "Burnout from working two jobs, can't sustain",
          probability: 10,
          value: -30,
          explanation:
            "Exhausted from job + business. Health suffers. Neither gets full attention. Abandon business. Time and energy wasted.",
        },
        {
          id: "biz-side-5",
          description:
            "Side project drags on indefinitely, never commit",
          probability: 5,
          value: -20,
          explanation:
            'Years of "someday I\'ll go full-time." Never feel ready. Business stays small. Opportunity cost of not committing.',
        },
      ],
    },
  ],
};

export const decisionTemplates: DecisionTemplate[] = [
  arrangedMarriageTemplate,
  careerTransitionTemplate,
  buyingHouseTemplate,
  startingBusinessTemplate,
];

/** Empty custom decision: 2 options × 3 scenarios, ready to edit. */
export function createCustomTemplate(): DecisionTemplate {
  const mkScenario = (
    n: number,
    description: string,
    probability: number,
    value: number
  ): Scenario => ({
    id: `custom-scenario-${Date.now()}-${n}`,
    description,
    probability,
    value,
  });

  const mkOption = (n: number): Option => ({
    id: `custom-option-${Date.now()}-${n}`,
    name: `Option ${n}`,
    description: "Describe this option in a sentence.",
    scenarios: [
      mkScenario(1, "Best case scenario for this option", 30, 80),
      mkScenario(2, "Most likely scenario for this option", 50, 20),
      mkScenario(3, "Worst case scenario for this option", 20, -40),
    ],
  });

  return {
    id: `custom-${Date.now()}`,
    title: "My custom decision (edit this title)",
    description:
      "Describe the decision you're facing, the context, and what's at stake (at least 20 characters).",
    category: "Custom",
    icon: "Sparkles",
    options: [mkOption(1), mkOption(2)],
  };
}
