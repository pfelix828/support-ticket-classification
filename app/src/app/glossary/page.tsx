export default function GlossaryPage() {
  const methods = [
    {
      term: "TF-IDF",
      aka: "Term Frequency–Inverse Document Frequency",
      plain: "A way to turn text into numbers that a computer can work with. It counts how often each word appears in a ticket, then gives extra weight to words that are rare across all tickets. So \"refund\" gets a high score because it mostly shows up in billing tickets — while \"the\" gets almost zero because it appears everywhere.",
      analogy: "Like highlighting the unusual words in a ticket and ignoring the common ones.",
    },
    {
      term: "Logistic Regression",
      aka: null,
      plain: "One of the simplest classification algorithms. It learns a weight for each word: \"refund\" pushes toward billing, \"login\" pushes toward account access. To classify a new ticket, it adds up all the word weights and picks the category with the highest total score.",
      analogy: "Like a scoring rubric — each keyword earns points for a category, and the category with the most points wins.",
    },
    {
      term: "XGBoost",
      aka: "Extreme Gradient Boosting",
      plain: "A more powerful classifier that builds hundreds of simple decision trees, each one correcting the mistakes of the previous ones. It can learn complex patterns like \"if the ticket mentions 'API' AND 'quota' but NOT 'how to', it's probably an API error rather than an API question.\"",
      analogy: "Like a team of specialists — each one learns from what the previous ones got wrong, and they vote together on the final answer.",
    },
    {
      term: "Embeddings",
      aka: "Vector representations",
      plain: "A way to represent text as a list of numbers (a \"vector\") that captures meaning, not just word counts. Tickets that mean similar things get similar vectors, even if they use completely different words. \"I can't sign in\" and \"unable to access my account\" would get nearly identical embeddings.",
      analogy: "Like placing every ticket on a map where similar tickets are close together — the computer can then draw boundaries between categories on that map.",
    },
    {
      term: "BERT",
      aka: "Bidirectional Encoder Representations from Transformers",
      plain: "A pre-trained language model from Google (2018) that reads text in both directions to understand context. It was trained on millions of documents and already \"understands\" English. Fine-tuning BERT means taking this pre-trained understanding and teaching it your specific task — like ticket classification.",
      analogy: "Like hiring someone who already speaks the language fluently, then training them on your specific job. They learn faster because they already understand the basics.",
    },
    {
      term: "Fine-Tuning",
      aka: null,
      plain: "Taking a model that already knows a lot (like GPT-4o-mini or BERT) and training it further on your specific data. The model keeps everything it already knows but adjusts its behavior to match your task. You show it thousands of examples — \"this ticket is billing, this one is API errors\" — and it learns the patterns.",
      analogy: "Like an experienced employee starting a new job — they already know how to work, they just need to learn your company's specific systems.",
    },
    {
      term: "Zero-Shot Classification",
      aka: null,
      plain: "Asking an LLM to classify tickets without showing it any examples first. You just describe the categories and say \"pick one.\" The model uses its general knowledge of language and support workflows to make a guess. No training data needed — you can start immediately.",
      analogy: "Like giving someone a job description and asking them to sort mail on their first day, with no training.",
    },
    {
      term: "Few-Shot Classification",
      aka: null,
      plain: "Same as zero-shot, but you include a few examples in the prompt: \"Here's a billing ticket, here's an API error ticket...\" The model learns the pattern from these demonstrations and applies it to new tickets. Typically 2-5 examples per category.",
      analogy: "Like showing the new hire a few example tickets before they start sorting — \"this kind of thing goes to billing, this kind goes to engineering.\"",
    },
    {
      term: "Distillation",
      aka: "Knowledge Distillation",
      plain: "Using a large, expensive, smart model (the \"teacher\") to label your data, then training a smaller, faster model (the \"student\") on those labels. The teacher can explain its reasoning — and the student learns that reasoning, not just the final answers. The student ends up much faster and cheaper to run, while capturing most of the teacher's intelligence.",
      analogy: "Like a senior expert training a junior employee — the junior learns not just what to do, but why. Then the junior handles the day-to-day work while the senior moves on.",
    },
    {
      term: "F1 Score",
      aka: "F1 Macro",
      plain: "The main metric we use to compare methods. It balances two things: how many of the tickets labeled \"billing\" are actually billing (precision), and how many actual billing tickets get caught (recall). F1 combines both into one number from 0% to 100%. \"Macro\" means we calculate F1 for each category separately and then average them — so rare categories like Security count just as much as common ones like Billing.",
      analogy: "Like a grade that penalizes both false alarms (calling something billing when it's not) and missed cases (letting a billing ticket slip through to the wrong team).",
    },
    {
      term: "Cascade Architecture",
      aka: null,
      plain: "Instead of using one model for everything, use a fast cheap model first. If it's confident, route the ticket immediately. If it's unsure, pass the ticket to a slower but smarter model. If even that model is unsure, send it to a human. This way, 75% of tickets get routed in milliseconds, and only the hard ones need the expensive model.",
      analogy: "Like a hospital triage system — the nurse handles routine cases, the doctor handles complicated ones, and the specialist handles the rare ones.",
    },
    {
      term: "LLM",
      aka: "Large Language Model",
      plain: "An AI model trained on massive amounts of text that can understand and generate human language. GPT-4o-mini is an LLM. These models have billions of parameters (internal settings) and can do many language tasks — classification, summarization, translation, conversation — without being specifically built for any one of them.",
      analogy: "Like a very well-read generalist who can turn their hand to most language tasks, versus a specialist tool built for one specific job.",
    },
    {
      term: "Confusion Pair",
      aka: null,
      plain: "Two categories that the model frequently mixes up. For example, \"API Usage\" and \"API Errors\" are a confusion pair because tickets like \"How do I fix 429 errors?\" could reasonably be either — it's a question (usage) about an error. Identifying confusion pairs tells you where to focus improvements.",
      analogy: "Like knowing that your mail room keeps mixing up packages for the 3rd and 4th floor — once you know the pattern, you can add better labels.",
    },
    {
      term: "Class Imbalance",
      aka: null,
      plain: "When some categories have way more tickets than others. In our dataset, Billing has ~16% of tickets while Security has ~1%. This matters because a model could get 99% accuracy on Security by simply never predicting it — which is useless. That's why we use F1 macro (which weights all categories equally) instead of raw accuracy.",
      analogy: "Like grading a student on 12 subjects but 8 of the questions are about math — if you only measure total score, you'd never know they're failing history.",
    },
  ];

  return (
    <div className="min-h-screen">
      <section className="px-12 pt-16 pb-8">
        <div className="max-w-4xl">
          <h1 className="text-3xl font-semibold tracking-tight" style={{ color: "var(--foreground)" }}>
            Glossary
          </h1>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl" style={{ color: "var(--foreground-secondary)" }}>
            Plain-language definitions for the methods and concepts used in this project.
            No PhD required.
          </p>
        </div>
      </section>

      <section className="px-12 pb-16">
        <div className="space-y-4">
          {methods.map((m) => (
            <div
              key={m.term}
              className="rounded-lg border p-5"
              style={{ backgroundColor: "var(--background-card)", borderColor: "var(--border)" }}
            >
              <div className="flex items-baseline gap-3 mb-2">
                <h2 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
                  {m.term}
                </h2>
                {m.aka && (
                  <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                    {m.aka}
                  </span>
                )}
              </div>
              <p className="text-sm leading-relaxed mb-3" style={{ color: "var(--foreground-secondary)" }}>
                {m.plain}
              </p>
              <div className="px-4 py-3 rounded-md" style={{ backgroundColor: "var(--background-secondary)" }}>
                <p className="text-xs leading-relaxed" style={{ color: "var(--foreground-muted)" }}>
                  <span className="font-medium" style={{ color: "var(--accent)" }}>Analogy: </span>
                  {m.analogy}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
