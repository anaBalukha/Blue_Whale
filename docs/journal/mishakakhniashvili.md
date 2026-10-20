# Pattern Journal - Mikheili Kakhniashvili

Updated retrospectively on 2026-10-19.

## Week 1 - Context as Budget

I applied this pattern by defining the essential conversation state
in docs/spec.md, including user requirements, decisions, and trusted
checkpoints. I delegated specification drafting and ambiguity review
to ChatGPT, then checked the suggestions against our MVP requirements.
I rejected building a web interface immediately because a terminal
application lets us test drift detection and recovery first.

## Week 2 - Spec Before Code

I applied this pattern to my individual Golden Test Evaluation Reporter,
writing testable acceptance criteria before implementing the feature.
I delegated the initial code and tests to ChatGPT and verified them
using pytest and CLI examples. Next time, I would include more
boundary cases in the specification from the beginning.

## Week 3 - Uncertainty-Aware UX

I considered how Blue Whale should handle ambiguous changes to
previously established requirements. The system should ask for
clarification rather than assume an uncertain change is approved.
The Lab 3 multimodal confidence feature is not yet implemented.
Next time, I would define and test the low-confidence route earlier.

## Week 4 - Grounded Generation

I worked on the retrieval corpus and golden evaluations for Blue Whale.
The offline run initially passed 1/5 cases; lowering the experimental
similarity threshold improved it to 4/5, but the two-document
reasoning case still failed. I verified the results by executing the
retrieval pipeline. Next time, I would test multi-document retrieval
earlier and compare the offline results with real-model results.
