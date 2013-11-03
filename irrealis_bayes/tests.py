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

  def test_get_total(self):
    self.assertEqual(5, self.pmf.get_total())

  def test_get_normalizer(self):
    self.assertTrue(0.199 < self.pmf.get_normalizer() < 0.201)

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
    test_copy

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
    test_cookie_problem

    Suppose there are two bowls of cookies. The first bowl contains 30 vanilla
    cookies and ten chocolate cookies. The second bowl contains twenty of each.
    Now suppose you choose one of the bowls at random and, without looking,
    select a cookie from bowl at random. The cookie is vanilla. What is the
    probability that it came from the first bowl?

    Prior to choosing the cookie, the probability P(bowl_1) of choosing the
    first bowl was 0.5 (since we were equally likely to choose either bowl).

    Assuming we had chosen the first bowl, the likelihood P(vanilla | bowl_1)
    of choosing a vanilla cookie was 0.75 (30 vanilla cookies out a total of
    forty cookies in the first bowl). On the other hand, assuming we had chosen
    the second bowl, the likelihood P(vanilla | bowl_2) of choosing a vanilla
    cookie was 0.5 (twenty vanilla cookies out of 40 cookies in the second
    bowl).

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
    test_cookie_problem_with_arbitrary_factors

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
      def likelihood(self, data, given):
        if given == data: return 0
        elif given == 'a': return 0.5
        else: return 1
        
    pmf = MontyHallProblem.fromkeys('abc', 1)
    pmf.update('b')
    self.assertTrue(0.333 < pmf['a'] < 0.334)
    self.assertTrue(0 <= pmf['b'] < 0.001)
    self.assertTrue(0.666 < pmf['c'] < 0.667)



if __name__ == "__main__": unittest.main()
