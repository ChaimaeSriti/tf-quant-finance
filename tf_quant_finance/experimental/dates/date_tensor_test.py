# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for date_tensor.py."""

import datetime
import numpy as np
import tensorflow as tf

from tf_quant_finance.experimental.dates import DateTensor
from tf_quant_finance.experimental.dates import PeriodTensor
from tf_quant_finance.experimental.dates import test_data
from tf_quant_finance.experimental.dates.constants import PeriodType
from tensorflow.python.framework import test_util  # pylint: disable=g-direct-tensorflow-import


@test_util.run_all_in_graph_and_eager_modes
class DateTensorTest(tf.test.TestCase):

  def test_create_from_date_time_list(self):
    dates = test_data.test_dates
    y, m, d, o, datetimes = unpack_test_dates(dates)
    date_tensor = DateTensor.from_datetimes(datetimes)
    self.assert_date_tensor_equals(date_tensor, y, m, d, o)

  def test_create_from_np_datetimes(self):
    dates = test_data.test_dates
    y, m, d, o, datetimes = unpack_test_dates(dates)
    np_datetimes = np.array(datetimes, dtype=np.datetime64)
    date_tensor = DateTensor.from_np_datetimes(np_datetimes)
    self.assert_date_tensor_equals(date_tensor, y, m, d, o)

  def test_create_from_tuples(self):
    dates = test_data.test_dates
    y, m, d, o, _ = unpack_test_dates(dates)
    date_tensor = DateTensor.from_tuples(dates)
    self.assert_date_tensor_equals(date_tensor, y, m, d, o)

  def test_create_from_year_month_day_tensors(self):
    dates = test_data.test_dates
    y, m, d, o, _ = unpack_test_dates(dates)
    date_tensor = DateTensor.from_year_month_day_tensors(y, m, d)
    self.assert_date_tensor_equals(date_tensor, y, m, d, o)

  def test_create_from_ordinals(self):
    dates = test_data.test_dates
    y, m, d, o, _ = unpack_test_dates(dates)
    date_tensor = DateTensor.from_ordinals(o)
    self.assert_date_tensor_equals(date_tensor, y, m, d, o)

  def test_validation(self):
    not_raised = []
    for y, m, d in test_data.invalid_dates:
      try:
        self.evaluate(DateTensor.from_tuples([(y, m, d)]).months())
        not_raised.append((y, m, d))
      except tf.errors.InvalidArgumentError:
        pass
    self.assertEmpty(not_raised)

    for invalid_ordinal in [-5, 0]:
      with self.assertRaises(tf.errors.InvalidArgumentError):
        self.evaluate(DateTensor.from_ordinals([invalid_ordinal]).months())

  def test_days_of_week(self):
    dates = test_data.test_dates
    datetimes = unpack_test_dates(dates)[-1]
    date_tensor = DateTensor.from_datetimes(datetimes)
    expected_days_of_week = np.array([dt.weekday() for dt in datetimes])
    self.assertAllEqual(expected_days_of_week, date_tensor.days_of_week())

  def test_days_until(self):
    dates = test_data.test_dates
    diffs = np.arange(0, len(dates))
    _, _, _, o, datetimes = unpack_test_dates(dates)
    date_tensor = DateTensor.from_datetimes(datetimes)

    target_ordinals = o + diffs
    target_datetimes = [datetime.date.fromordinal(o) for o in target_ordinals]
    target_date_tensor = DateTensor.from_datetimes(target_datetimes)
    self.assertAllEqual(diffs, date_tensor.days_until(target_date_tensor))

  def test_days_addition(self):
    self.perform_addition_test(test_data.day_addition_data, PeriodType.DAY)

  def test_week_addition(self):
    self.perform_addition_test(test_data.week_addition_data, PeriodType.WEEK)

  def test_month_addition(self):
    self.perform_addition_test(test_data.month_addition_data, PeriodType.MONTH)

  def test_year_addition(self):
    self.perform_addition_test(test_data.year_addition_data, PeriodType.YEAR)

  def perform_addition_test(self, data, period_type):
    dates_from, quantities, expected_dates = [], [], []
    for date_from, quantity, expected_date in data:
      dates_from.append(date_from)
      quantities.append(quantity)
      expected_dates.append(expected_date)

    datetimes = unpack_test_dates(dates_from)[-1]
    date_tensor = DateTensor.from_datetimes(datetimes)
    period_tensor = PeriodTensor(quantities, period_type)
    result_date_tensor = date_tensor + period_tensor

    y, m, d, o, _ = unpack_test_dates(expected_dates)
    self.assert_date_tensor_equals(result_date_tensor, y, m, d, o)

  def test_date_subtraction(self):
    # Subtraction trivially transforms to addition, so we don't test
    # extensively.
    dates_from = DateTensor.from_tuples([(2020, 3, 15), (2020, 3, 31)])
    period = PeriodTensor([2, 1], PeriodType.MONTH)
    expected_ordinals = np.array([datetime.date(2020, 1, 15).toordinal(),
                                  datetime.date(2020, 2, 29).toordinal()])
    self.assertAllEqual(expected_ordinals, (dates_from - period).ordinals())

  def assert_date_tensor_equals(self, date_tensor, years_np, months_np, days_np,
                                ordinal_np):
    self.assertAllEqual(years_np, date_tensor.years())
    self.assertAllEqual(months_np, date_tensor.months())
    self.assertAllEqual(days_np, date_tensor.days())
    self.assertAllEqual(ordinal_np, date_tensor.ordinals())

  def test_comparisons(self):
    dates1 = DateTensor.from_tuples([(2020, 3, 15),
                                     (2020, 3, 31),
                                     (2021, 2, 28)])
    dates2 = DateTensor.from_tuples([(2020, 3, 18),
                                     (2020, 3, 31),
                                     (2019, 2, 28)])
    self.assertAllEqual(np.array([False, True, False]), dates1 == dates2)
    self.assertAllEqual(np.array([True, False, True]), dates1 != dates2)
    self.assertAllEqual(np.array([False, False, True]), dates1 > dates2)
    self.assertAllEqual(np.array([False, True, True]), dates1 >= dates2)
    self.assertAllEqual(np.array([True, False, False]), dates1 < dates2)
    self.assertAllEqual(np.array([True, True, False]), dates1 <= dates2)

  def test_tensor_wrapper_ops(self):
    dates1 = DateTensor.from_tuples([(2019, 3, 25), (2020, 1, 2), (2019, 1, 2)])
    dates2 = DateTensor.from_tuples([(2019, 4, 25), (2020, 5, 2), (2018, 1, 2)])
    dates = DateTensor.stack((dates1, dates2), axis=-1)
    self.assertEqual((3, 2), dates.shape)
    self.assertEqual((2,), dates[0].shape)
    self.assertEqual((2, 2), dates[1:].shape)
    self.assertEqual((2, 1), dates[1:, :-1].shape)
    self.assertEqual((3, 1, 2), dates.expand_dims(axis=1).shape)
    self.assertEqual((3, 3, 2), dates.broadcast_to((3, 3, 2)).shape)


def unpack_test_dates(dates):
  y, m, d = (np.array([d[i] for d in dates], dtype=np.int32) for i in range(3))
  datetimes = [datetime.date(y, m, d) for y, m, d in dates]
  o = np.array([datetime.date(y, m, d).toordinal() for y, m, d in dates],
               dtype=np.int32)
  return y, m, d, o, datetimes

if __name__ == '__main__':
  tf.test.main()
