'''
Probability mass function (PMF) and cumulative distribution function (CDF)
classes for use in study of Allen B. Downey's "Think Bayes: Bayesian Statistics
Made Simple", version 1.0.1.
'''
import bisect, random


def filter_possible_events(pmf):
  return PMF((event, prob) for event, prob in pmf.iteritems() if 0 < prob)

def add_two_independent_pmfs(left_pmf, right_pmf):
  left_pmf, right_pmf = [filter_possible_events(pmf) for pmf in (left_pmf, right_pmf)]
  result = PMF()
  for left_event, left_prob in left_pmf.iteritems():
    for right_event, right_prob in right_pmf.iteritems():
      sum_event = left_event + right_event
      result[sum_event] = result.get(sum_event, 0.) + left_prob*right_prob
  return result

def sum_independent_pmfs(pmfs):
  return reduce(lambda x, y: x+y, pmfs)


class PMF(dict):
  'Dictionary as probability mass function.'
  def __init__(self, *al, **kw):
    super(PMF, self).__init__(*al, **kw)

  def __add__(self, other):
    return add_two_independent_pmfs(self, other)

  def copy(self):
    'Return a shallow copy of this distribution.'
    return self.__class__(self)

  def total(self):
    'Sum elements of this distribution.'
    return sum(self.itervalues())

  def normalizer(self):
    'Return normalizing constant to scale distribution so it sums to one.'
    total = self.total()
    return 1./total if total else float('inf')

  def expectation(self):
    'Compute the expectation, aka mean, of this distribution.'
    try:
      return sum(event*prob for event, prob in self.iteritems())
    except TypeError as e:
      raise TypeError("Can't compute expectation of non-numeric events ({})".format(e))

  def scale(self, factor):
    'Scale all measures by a common factor.'
    for key in self:
      self[key] *= factor

  def normalize(self):
    'Normalize all measures so they sum to one, making this a probability distribution.'
    self.scale(self.normalizer())

  def random(self):
    '''
    Returns random event.
    Probability of returning this event is determined by this distribution.
    '''
    # It would be nice if we didn't have to compute total every time this
    # function is called; but otherwise we'd have to assume this distribution
    # has been normalized(), which is not always true.
    #
    # I've considered keeping a 'total' attribute which is always up-to-date.
    # Might be worth doing; but increases code complexity.
    target = random.random()*self.total()
    total = 0
    for event, prob in self.iteritems():
      total += prob
      if total >= target:
        return event

  def uniform_dist(self, events):
    'Assign equal probabilities to each of a list of events.'
    self.clear()
    for event in events:
      self[event] = 1
    self.normalize()

  def power_law_dist(self, events, alpha=1.):
    'Assign power law distribution to each of a list of quantitative events.'
    self.clear()
    for event in events:
      self[event] = event**(-alpha)
    self.normalize()

  def update(self, data):
    'Updates posterior probability distribution given new data.'
    for event in self:
      self[event] *= self.likelihood(data, given = event)
    self.normalize()

  def likelihood(self, data, given):
    '''
    Returns likelihood of observed data given a event. Unimplemented.
    Should be implemented in subclasses.
    '''
    raise NotImplementedError


def dict_items_from_data(data):
  'Convert data into a dict, then return its elements as key-value pairs.'
  return dict(data if data else []).items()

def first_element(l):
  'Return the first element of l.'
  return l[0]

def sort_items(items, cmp=None, key=None, reverse=False):
  '''
  Sort item list in-place.
  By default, expects list of dict key-value pairs, and sorts pairs on value.
  '''
  items.sort(cmp=cmp, key=key if key else first_element, reverse=reverse)

def running_sum(l):
  'Generator function to return an iterable running sum of l (which can itself be any iterable).'
  total = 0
  for x in l:
    total += x
    yield total


class CDF(object):
  'Discrete cumulative distribution function.'
  def __init__(self, data=None, cmp=None, key=None, reverse=False):
    items = dict_items_from_data(data)
    sort_items(items, cmp, key, reverse)
    self.events, probabilities = zip(*items)
    self.cumulative_distribution = tuple(running_sum(probabilities))

  def floor_index(self, probability):
    'Get index of last event at or below given percentile (specified as probability).'
    index = bisect.bisect(self.cumulative_distribution, probability)
    return index-1 if probability==self.cumulative_distribution[index-1] else index

  def percentile(self, probability):
    'Return event corresponding to percentile (specified as probability).'
    return self.events[self.floor_index(probability)]

  def percentiles(self, *probabilities):
    '''
    Return list of event corresponding list of percentiles (specified as probabilities).
    Use this to obtain a credible interval; for example, to get the 90%
    interval between the fifth and 95th percentiles, write:

    credible_interval = cdf.percentiles(0.05, 0.95)
    '''
    return tuple(self.percentile(probability) for probability in probabilities)
