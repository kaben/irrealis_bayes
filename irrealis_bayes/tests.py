# -*- coding: utf-8 -*-
from irrealis_bayes import PMF, BayesPMF

import unittest


class UnitTestPMF(unittest.TestCase):
  def setUp(self):
    self.pmf = PMF(dict.fromkeys('abcde', 1))

  def exercise_pmf(self):
    self.pmf.normalize()
    # Should have six entries corresponding to 'a' through 'f'.
    self.assertEqual(5, len(self.pmf))
    # Sum should be one to within rounding error.
    self.assertTrue(0.999 < sum(self.pmf.itervalues()) < 1.001)

  def test_total(self):
    self.assertEqual(5, self.pmf.total())

  def test_normalizer(self):
    self.assertTrue(0.199 < self.pmf.normalizer() < 0.201)

  def test_mean(self):
    pmf = PMF.fromkeys((1,2,3), 1.)
    pmf.normalize()
    self.assertTrue(1.999 < pmf.mean() < 2.001)

  def test_mean_raises_on_nonnumeric_hypothesis(self):
    with self.assertRaises(TypeError): self.pmf.mean()

  def test_ints(self):
    self.exercise_pmf()

  def test_floats(self):
    self.pmf = PMF.fromkeys('abcde', 1.)
    self.exercise_pmf()

  def test_zerosum(self):
    self.pmf = PMF.fromkeys('abcde', 0)
    self.pmf.normalize()
    total = sum(self.pmf.itervalues())
    # This is how we verify total is 'nan': only 'nan' is not equal to itself.
    self.assertNotEqual(total, total)

  def test_copy(self):
    '''
    test_copy (irrealis_bayes.tests.UnitTestPMF)

    Verify that pmf.copy() copies data into a new, independent PMF instance.
    '''
    pmf2 = self.pmf.copy()
    pmf2.normalize()
    for key in self.pmf:
      self.assertEqual(1, self.pmf[key])
      self.assertTrue(0.199 < pmf2[key] < 0.201)


class FunctionalTestPMF(unittest.TestCase):
  def test_cookie_problem(self):
    '''
    test_cookie_problem (irrealis_bayes.tests.FunctionalTestPMF)

    From Think Bayes:

      Suppose there are two bowls of cookies. The first bowl contains 30
      vanilla cookies and ten chocolate cookies. The second bowl contains
      twenty of each.  Now suppose you choose one of the bowls at random and,
      without looking, select a cookie from bowl at random. The cookie is
      vanilla. What is the probability that it came from the first bowl?

      Prior to choosing the cookie, the probability P(bowl_1) of choosing the
      first bowl was 0.5 (since we were equally likely to choose either bowl).

      Assuming we had chosen the first bowl, the likelihood P(vanilla | bowl_1)
      of choosing a vanilla cookie was 0.75 (30 vanilla cookies out a total of
      forty cookies in the first bowl). On the other hand, assuming we had
      chosen the second bowl, the likelihood P(vanilla | bowl_2) of choosing a
      vanilla cookie was 0.5 (twenty vanilla cookies out of 40 cookies in the
      second bowl).

      Since our hypotheses (bowl one or bowl two) are exclusive and exhaustive,
      the law of total probability gives:
      
        P(bowl_1 | vanilla)
        = (P(bowl_1)*P(vanilla | bowl_1)) / (P(bowl_1)*P(vanilla | bowl_1) + P(bowl_2)*P(vanilla | bowl_2))
        = (0.5*0.75)/(0.5*0.75 + 0.5*0.5)
        = (0.75)/(0.75 + 0.5)
        = 0.6
    '''
    pmf = PMF(bowl_1 = 0.5, bowl_2 = 0.5)
    pmf['bowl_1'] *= 0.75
    pmf['bowl_2'] *= 0.5
    pmf.normalize()
    self.assertTrue(0.599 < pmf['bowl_1'] < 0.601)

  def test_cookie_problem_with_arbitrary_factors(self):
    '''
    test_cookie_problem_with_arbitrary_factors (irrealis_bayes.tests.FunctionalTestPMF)

    Can multiply dictionary by any convenient factor, as long as the whole
    dictionary is multiplied by that factor. We later normalize to get a
    probability distribution.
    '''
    # One "bowl_1" and one "bowl_2".
    pmf = PMF(bowl_1 = 1, bowl_2 = 1)
    # Thirty vanilla cookies (out of forty) in bowl_1.
    pmf['bowl_1'] *= 30
    # Twenty vanilla cookies (out of forty) in bowl_2.
    pmf['bowl_2'] *= 20
    # This normalizes dictionary into a probability distribution.
    pmf.normalize()
    self.assertTrue(0.599 < pmf['bowl_1'] < 0.601)


class FunctionalTestBayesPMF(unittest.TestCase):
  def test_unimplemented_likelihood_raises(self):
    pmf = BayesPMF(x = 2)
    with self.assertRaises(NotImplementedError): pmf.update('blah')

  def test_monty_hall_problem(self):
    '''
    test_monty_hall_problem (irrealis_bayes.tests.FunctionalTestBayesPMF)

    From Think Bayes:

      The Monty Hall problem might be the most contentious question in the
      his-tory of probability. The scenario is simple, but the correct answer
      is so counterintuitive that many people just can't accept it, and many
      smart people have embarrassed themselves not just by getting it wrong but
      by arguing the wrong side, aggressively, in public.

      Monty Hall was the original host of the game show Let's Make a Deal. The
      Monty Hall problem is based on one of the regular games on the show. If
      you are on the show, here's what happens:

      - Monty shows you three closed doors and tells you that there is a prize
        behind each door: one prize is a car, the other two are less valuable
        prizes like peanut butter and fake finger nails. The prizes are
        arranged at random.

      - The object of the game is to guess which door has the car.  If you
        guess right, you get to keep the car.

      - You pick a door, which we will call Door A. We'll call the other doors
        B and C.

      - Before opening the door you chose, Monty increases the suspense by
        opening either Door B or C, whichever does not have the car. (If the
        car is actually behind Door A, Monty can safely open B or C, so he
        chooses one at random.)

      - Then Monty offers you the option to stick with your original choice or
        switch to the one remaining unopened door.
       
      The question is, should you “stick” or “switch” or does it make no
      difference?

      Most people have the strong intuition that it makes no difference. There
      are two doors left, they reason, so the chance that the car is behind
      Door A is 50%.

      But that is wrong. In fact, the chance of winning if you stick with Door
      A is only 1/3; if you switch, your chances are 2/3.
    '''
    class MontyHallProblem(BayesPMF):
      def __init__(self, *al, **kw):
        super(MontyHallProblem, self).__init__(*al, **kw)
      def likelihood(self, data, given_hypothesis):
        if given_hypothesis == data: return 0
        elif given_hypothesis == 'a': return 0.5
        else: return 1
        
    pmf = MontyHallProblem()
    pmf.uniform_priors('abc')
    pmf.update('b')
    self.assertTrue(0.333 < pmf['a'] < 0.334)
    self.assertTrue(0 <= pmf['b'] < 0.001)
    self.assertTrue(0.666 < pmf['c'] < 0.667)

  def test_cookie_problem(self):
    '''
    test_cookie_problem (irrealis_bayes.tests.FunctionalTestBayesPMF)

    As in previous example, but using BayesPMF subclass with likelihood().
    implemented.
    '''
    class CookieProblem(BayesPMF):
      def __init__(self, *al, **kw):
        super(CookieProblem, self).__init__(*al, **kw)
        self.hypotheses = dict(
          bowl_1 = PMF(vanilla = 30, chocolate = 10),
          bowl_2 = PMF(vanilla = 20, chocolate = 20),
        )
        self.uniform_priors(self.hypotheses)
      def likelihood(self, data, given_hypothesis):
        return self.hypotheses[given_hypothesis][data]
        
    pmf = CookieProblem()
    pmf.update('vanilla')
    self.assertTrue(0.599 < pmf['bowl_1'] < 0.601)

  def test_MnM_problem(self):
    '''
    test_MnM_problem (irrealis_bayes.tests.FunctionalTestBayesPMF)
    
    From Think Bayes:

      In 1995, they introduced blue M&M's. Before then, the color mix in a bag
      of plain M&M's was 30% Brown, 20% Yellow, 20% Red, 10% Green, 10% Orange,
      10% Tan. Afterward it was 24% Blue, 20% Green, 16% Orange, 14% Yellow,
      13% Red, 13% Brown.

      Suppose a friend of mine has two bags of M&M's, and he tells me that one
      is from 1994 and one from 1996. He won't tell me which is which, but he
      gives me one M&M from each bag. One is yellow and one is green. What is
      the probability that the yellow one came from the 1994 bag?
    '''
    class MnMProblem(BayesPMF):
      def __init__(self, *al, **kw):
        super(MnMProblem, self).__init__(*al, **kw)
        mix94 = PMF(brown=30, yellow=20, red=20, green=10, orange=10, tan=10)
        mix96 = PMF(blue=24, green=20, orange=16, yellow=14, red=13, brown=13)
        self.hypotheses = dict(
          A = dict(bag_1 = mix94, bag_2 = mix96),
          B = dict(bag_1 = mix96, bag_2 = mix94),
        )
        self.uniform_priors(self.hypotheses)
      def likelihood(self, data, given_hypothesis):
        bag, color = data
        return self.hypotheses[given_hypothesis][bag][color]
        
    pmf = MnMProblem()
    pmf.update(('bag_1', 'yellow'))
    pmf.update(('bag_2', 'green'))
    self.assertTrue(0.740 < pmf['A'] < 0.741)

  def test_cookie_problem_sans_replacement(self):
    '''
    test_cookie_problem_sans_replacement (irrealis_bayes.tests.FunctionalTestBayesPMF)

    As before, two cookie bowls, the first containing 30 vanilla and ten
    chocolate cookies, the second twenty of each. You choose one of the bowls
    at random and, without looking, select a random cookie from the bowl. The
    cookie is vanilla. What is the probability it came from the first bowl?

    P(vanilla) = P(bowl_1)*P(vanilla|bowl_1) + P(bowl_2)*P(vanilla|bowl_2)

    P(bowl_1|vanilla) = P(bowl_1)*P(vanilla|bowl_1)/P(vanilla)

    = (0.5*0.75)/(0.5*0.75 + 0.5*0.5)
    = (0.75)/(0.75 + 0.5)
    = 0.6

    Now, without putting the first cookie back, take a second cookie from the
    same bowl. The cookie is again vanilla. What is the new probability that it
    came from the first bowl?

    The problem is very similar, but our previous posterior probabilities have
    become our new prior probabilities, and our likelihoods have also changed:

      P(bowl_1) = 0.6
      P(bowl_2) = 0.4
      P(vanilla | bowl_1) = 29/39 ~= 0.744
      P(vanilla | bowl_2) = 19/39 ~= 0.487
      P(bowl_1 | vanilla) = (0.6*0.744)/(0.6*0.744 + 0.4*0.487)
      ~= 0.696
    '''
    class CookieProblem(BayesPMF):
      '''
      We have two hypotheses:
      - A: bowl_a is bowl_1 (30 vanilla, 10 chocolate),
        and bowl_b is bowl_2 (20 vanilla, 20 chocolate).
      - B: bowl_a is bowl_2 (20 vanilla, 20 chocolate),
        and bowl_b is bowl_1 (30 vanilla, 10 chocolate).
      
      As we gather data, we update each hypothesis. For example, if we choose a
      vanilla cookie from bowl a, then our new hypotheses are:
      - A: bowl_a is bowl_1 (29 vanilla, 10 chocolate),
        and bowl_b is bowl_2 (20 vanilla, 20 chocolate).
      - B: bowl_a is bowl_2 (19 vanilla, 20 chocolate),
        and bowl_b is bowl_1 (30 vanilla, 10 chocolate).
      
      Since the total numbers of cookies in each bowl are now different, we
      must normalize the distributions in each hypothesis before computing
      likelihoods. But if we were to normalize the state variables of each
      hypothesis, we wouldn't be able to update hypotheses anymore. So instead
      of normalizing the distributions in the state variables of hypotheses, we
      make normalized copies of the distributions, and use these copies for
      computing likelihoods.
      '''
      def __init__(self, *al, **kw):
        super(CookieProblem, self).__init__(*al, **kw)
        # These encode the initial state of the bowls.
        bowl_1 = PMF(vanilla=30, chocolate=10)
        bowl_2 = PMF(vanilla=20, chocolate=20)
        self.hypotheses = dict(
          # The states of the different hypotheses mustn't depend on each
          # other, so each hypothesis gets its own copy of the initial state.
          A = dict(bowl_a = bowl_1.copy(), bowl_b = bowl_2.copy()),
          B = dict(bowl_a = bowl_2.copy(), bowl_b = bowl_1.copy()),
        )
        self.uniform_priors(self.hypotheses)
      def likelihood(self, data, given_hypothesis):
        bowl, cookie = data
        # First we obtain a copy of the distribution for given hypothesis.
        distribution = self.hypotheses[given_hypothesis][bowl].copy()
        # The we normalize the copy so we can compute the likelihood.
        distribution.normalize()
        likelihood = distribution[cookie]
        # Then we update the state of the hypothesis.
        self.hypotheses[given_hypothesis][bowl][cookie] -= 1
        # Now we can return the computed likelihood.
        return likelihood

    pmf = CookieProblem()
    pmf.update(('bowl_a', 'vanilla'))
    self.assertTrue(0.599 < pmf['A'] < 0.601)
    pmf.update(('bowl_a', 'vanilla'))
    self.assertTrue(0.696 < pmf['A'] < 0.697)

  def test_dice_problem(self):
    '''
    test_dice_problem (irrealis_bayes.tests.FunctionalTestBayesPMF)

    From Think Bayes:
    
      Suppose I have a box of dice that contains a 4-sided die, a 6-sided die,
      an 8-sided die, a 12-sided die, and a 20-sided die. If you have ever
      played Dungeons & Dragons, you know what I am talking about.

      Suppose I select a die from the box at random, roll it, and get a 6. What
      is the probability that I rolled each die?

      Let me suggest a three-step strategy for approaching a problem like this:
      - Choose a representation for the hypotheses.
      - Choose a representation for the data.
      - Write a likelihood function.

    In this case, Downey chooses the numbers [4, 6, 8, 12, 20] to represent
    hypotheses, and integers one through twenty to represent data. These
    representations are chosen to make the likelihood function easy to write:
    '''
    # The likelihood of a roll (our data) greater than the number of sides of a
    # given die (our hypothesis) is zero; in other words, P(data|hypothesis) =
    # 0 if hypothesis < data). Otherwise, the likelihood of seeing any side of
    # an N-sided die is 1/N.
    class DiceProblem(BayesPMF):
      def likelihood(self, data, given_hypothesis):
        return 0 if given_hypothesis < data else 1./given_hypothesis

    pmf = DiceProblem()
    pmf.uniform_priors([4,6,8,12,20])

    pmf.update(6)
    self.assertEqual(0., pmf[4])
    self.assertTrue(0.392 < pmf[6] < 0.393)
    self.assertTrue(0.294 < pmf[8] < 0.295)
    self.assertTrue(0.196 < pmf[12] < 0.197)
    self.assertTrue(0.117 < pmf[20] < 0.118)

    for roll in (6,8,7,7,5,4): pmf.update(roll)
    self.assertEqual(0., pmf[4])
    self.assertEqual(0., pmf[6])
    self.assertTrue(0.943 < pmf[8] < 0.944)
    self.assertTrue(0.055 < pmf[12] < 0.056)
    self.assertTrue(0.001 < pmf[20] < 0.002)

  def test_locomotive_problem(self):
    '''
    test_locomotive_problem (irrealis_bayes.tests.FunctionalTestBayesPMF)

    From Think Bayes:
    
      "A railroad numbers its locomotives in order 1..N. One day you see a
      locomotive with the number 60. Estimate how many locomotives the railroad
      has."

      Based on this observation, we know the railroad has 60 or more
      locomotives. But how many more? To apply Bayesian reasoning, we can break
      this problem into two steps:
      - What did we know about N before we saw the data?
      - For any given value of N, what is the likelihood of seeing the data (a
        locomotive with the number 60)?

      The answer to the first question is the prior. The answer to the second
      is the likelihood.
    '''
    # The likelihood function is identical to that of the dice problem.
    class LocomotiveProblem(BayesPMF):
      def likelihood(self, data, given_hypothesis):
        return 0 if given_hypothesis < data else 1./given_hypothesis

    # We don't have much basis to choose a prior, but we can start with
    # something simple and then consider alternatives. Let's assume that N is
    # equally likely to be any value from 1 to 1000.
    pmf = LocomotiveProblem()
    pmf.uniform_priors(xrange(1, 1001))
    pmf.update(60)
    most_likely_hypothesis, max_likelihood = max(pmf.iteritems(), key = lambda x: x[1])

    # The most likely hypothesis is 60 locomotives. That might not seem like a
    # very good guess; after all, what are the chances that you just happened
    # to see the train with the highest number? Nevertheless, if you want to
    # maximize the chance of getting the number exactly right, you should guess
    # 60:
    self.assertEqual(60, most_likely_hypothesis)
    self.assertTrue(0.005 < max_likelihood < 0.006)

    # That might not be the right goal. An alternative is to compute the mean
    # of the posterior distribution:
    self.assertTrue(333 < pmf.mean() < 334)


if __name__ == "__main__": unittest.main()
