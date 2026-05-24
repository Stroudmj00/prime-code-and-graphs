#include <algorithm>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

using u64 = std::uint64_t;
using u128 = unsigned __int128;

static constexpr u64 small_primes[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};

static u64 parse_u64(const char* text) {
	u64 value = 0;
	for (const char* cursor = text; *cursor != '\0'; ++cursor) {
		if (*cursor == '_' || *cursor == ',') {
			continue;
		}
		if (*cursor < '0' || *cursor > '9') {
			throw std::invalid_argument("expected an unsigned integer");
		}
		const u64 digit = static_cast<u64>(*cursor - '0');
		if (value > (std::numeric_limits<u64>::max() - digit) / 10) {
			throw std::overflow_error("unsigned integer is too large");
		}
		value = value * 10 + digit;
	}
	return value;
}

static u64 ordinal_from_zero_index(u64 n_zero_indexed) {
	if (n_zero_indexed == std::numeric_limits<u64>::max()) {
		throw std::overflow_error("prime index is too large");
	}
	return n_zero_indexed + 1;
}

static u64 checked_estimate_to_u64(long double estimate) {
	if (!std::isfinite(estimate) || estimate < 0.0L) {
		throw std::overflow_error("nth-prime estimate is out of range");
	}
	constexpr long double max_u64 = static_cast<long double>(std::numeric_limits<u64>::max());
	if (estimate > max_u64) {
		throw std::overflow_error("nth-prime estimate exceeds uint64 range");
	}
	return static_cast<u64>(estimate);
}

static u64 upper_bound_for_nth_prime(u64 n_zero_indexed) {
	if (n_zero_indexed < 6) {
		return 16;
	}
	const long double n = static_cast<long double>(ordinal_from_zero_index(n_zero_indexed));
	const long double estimate = n * (std::log(n) + std::log(std::log(n))) + 32.0L;
	return checked_estimate_to_u64(estimate);
}

static u64 axler_upper_bound_for_nth_prime(u64 n_zero_indexed) {
	if (n_zero_indexed < 6) {
		return 16;
	}
	const u64 ordinal = ordinal_from_zero_index(n_zero_indexed);
	if (ordinal < 46'254'381ULL) {
		return upper_bound_for_nth_prime(n_zero_indexed);
	}
	const long double n = static_cast<long double>(ordinal);
	const long double log_n = std::log(n);
	const long double log_log_n = std::log(log_n);
	const long double inverse_log = 1.0L / log_n;
	const long double estimate =
		n * (
			log_n + log_log_n - 1.0L +
			(log_log_n - 2.0L) * inverse_log -
			((log_log_n * log_log_n - 6.0L * log_log_n + 10.667L) * 0.5L * inverse_log * inverse_log)
		);
	return checked_estimate_to_u64(estimate + 32.0L);
}

static u64 lower_bound_for_nth_prime(u64 n_zero_indexed) {
	if (n_zero_indexed < 6) {
		return 0;
	}
	const long double n = static_cast<long double>(ordinal_from_zero_index(n_zero_indexed));
	const long double log_n = std::log(n);
	const long double log_log_n = std::log(log_n);
	const long double estimate = n * (log_n + log_log_n - 1.0L + (log_log_n - 2.1L) / log_n);
	if (estimate <= 0.0L) {
		return 0;
	}
	return checked_estimate_to_u64(estimate);
}

static u64 axler_lower_bound_for_nth_prime(u64 n_zero_indexed) {
	if (n_zero_indexed < 6) {
		return 0;
	}
	const u64 ordinal = ordinal_from_zero_index(n_zero_indexed);
	if (ordinal < 46'254'381ULL) {
		return lower_bound_for_nth_prime(n_zero_indexed);
	}
	const long double n = static_cast<long double>(ordinal);
	const long double log_n = std::log(n);
	const long double log_log_n = std::log(log_n);
	const long double inverse_log = 1.0L / log_n;
	const long double estimate =
		n * (
			log_n + log_log_n - 1.0L +
			(log_log_n - 2.0L) * inverse_log -
			((log_log_n * log_log_n - 6.0L * log_log_n + 11.321L) * 0.5L * inverse_log * inverse_log)
		);
	if (estimate <= 0.0L) {
		return 0;
	}
	return checked_estimate_to_u64(estimate);
}

static u64 approximate_nth_prime(u64 n_zero_indexed) {
	if (n_zero_indexed < 6) {
		return 16;
	}
	const long double n = static_cast<long double>(ordinal_from_zero_index(n_zero_indexed));
	const long double log_n = std::log(n);
	const long double log_log_n = std::log(log_n);
	const long double inverse_log = 1.0L / log_n;
	const long double correction =
		log_n + log_log_n - 1.0L +
		(log_log_n - 2.0L) * inverse_log -
		((log_log_n * log_log_n - 6.0L * log_log_n + 11.0L) * 0.5L * inverse_log * inverse_log);
	const long double estimate = n * correction;
	if (estimate <= 0.0L) {
		return 0;
	}
	return checked_estimate_to_u64(estimate);
}

static u64 isqrt_floor(u64 value) {
	u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(value)));
	while ((root + 1) <= value / (root + 1)) {
		++root;
	}
	while (root > value / root) {
		--root;
	}
	return root;
}

static u64 icbrt_floor(u64 value) {
	u64 root = static_cast<u64>(std::cbrt(static_cast<long double>(value)));
	while (static_cast<u128>(root + 1) * (root + 1) * (root + 1) <= value) {
		++root;
	}
	while (static_cast<u128>(root) * root * root > value) {
		--root;
	}
	return root;
}

static bool is_prime_naive(u64 n) {
	if (n < 2) {
		return false;
	}
	for (u64 d = 2; d < n; ++d) {
		if (n % d == 0) {
			return false;
		}
	}
	return true;
}

static bool is_prime_sqrt(u64 n) {
	if (n < 2) {
		return false;
	}
	if (n % 2 == 0) {
		return n == 2;
	}
	for (u64 d = 3; d <= n / d; d += 2) {
		if (n % d == 0) {
			return false;
		}
	}
	return true;
}

static u64 mod_pow(u64 base, u64 exp, u64 mod) {
	u64 result = 1;
	while (exp > 0) {
		if (exp & 1) {
			result = static_cast<u64>((static_cast<u128>(result) * base) % mod);
		}
		base = static_cast<u64>((static_cast<u128>(base) * base) % mod);
		exp >>= 1;
	}
	return result;
}

static bool miller_rabin_witness(u64 n, u64 base, u64 d, unsigned s) {
	if (base % n == 0) {
		return false;
	}
	u64 x = mod_pow(base % n, d, n);
	if (x == 1 || x == n - 1) {
		return false;
	}
	for (unsigned r = 1; r < s; ++r) {
		x = static_cast<u64>((static_cast<u128>(x) * x) % n);
		if (x == n - 1) {
			return false;
		}
	}
	return true;
}

static bool is_prime_miller_rabin(u64 n) {
	if (n < 2) {
		return false;
	}
	for (const u64 p : small_primes) {
		if (n == p) {
			return true;
		}
		if (n % p == 0) {
			return false;
		}
	}

	u64 d = n - 1;
	unsigned s = 0;
	while ((d & 1) == 0) {
		d >>= 1;
		++s;
	}

	const auto test_bases = [&](const u64* bases, std::size_t count) {
		for (std::size_t i = 0; i < count; ++i) {
			if (miller_rabin_witness(n, bases[i], d, s)) {
				return false;
			}
		}
		return true;
	};

	// Jaeschke-style deterministic base tiers used by the reference notes.
	// The final tier keeps the broad 64-bit fallback for values beyond those ranges.
	constexpr u64 bases_5k[] = {377687};
	constexpr u64 bases_19m[] = {2, 299417};
	constexpr u64 bases_4b[] = {2, 7, 61};
	constexpr u64 bases_1t[] = {2, 13, 23, 1662803};
	constexpr u64 bases_341t[] = {2, 3, 5, 7, 11, 13, 17};
	constexpr u64 bases_64[] = {2, 325, 9375, 28178, 450775, 9780504, 1795265022};

	if (n < 5329) {
		return test_bases(bases_5k, std::size(bases_5k));
	}
	if (n < 19471033) {
		return test_bases(bases_19m, std::size(bases_19m));
	}
	if (n < 4759123141ULL) {
		return test_bases(bases_4b, std::size(bases_4b));
	}
	if (n < 1122004669633ULL) {
		return test_bases(bases_1t, std::size(bases_1t));
	}
	if (n < 341550071728321ULL) {
		return test_bases(bases_341t, std::size(bases_341t));
	}
	return test_bases(bases_64, std::size(bases_64));
}

template <typename Predicate>
static u64 nth_prime_by_iteration(u64 n, Predicate is_prime) {
	u64 count = 0;
	for (u64 candidate = 2;; ++candidate) {
		if (is_prime(candidate)) {
			if (count == n) {
				return candidate;
			}
			++count;
		}
	}
}

static u64 nth_prime_sieve_erat(u64 n) {
	u64 bound = upper_bound_for_nth_prime(n);

	for (;;) {
		std::vector<bool> composite(bound + 1, false);
		for (u64 p = 2; p <= bound / p; ++p) {
			if (!composite[p]) {
				for (u64 multiple = p * p; multiple <= bound; multiple += p) {
					composite[multiple] = true;
				}
			}
		}

		u64 count = 0;
		for (u64 candidate = 2; candidate <= bound; ++candidate) {
			if (!composite[candidate]) {
				if (count == n) {
					return candidate;
				}
				++count;
			}
		}

		bound *= 2;
	}
}

static u64 nth_prime_sieve_erat_odd(u64 n) {
	if (n == 0) {
		return 2;
	}

	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const auto odd_count = static_cast<std::size_t>((bound - 1) / 2);
		std::vector<bool> composite(odd_count, false);

		for (u64 p = 3; p <= bound / p; p += 2) {
			if (!composite[static_cast<std::size_t>((p - 3) / 2)]) {
				for (u64 multiple = p * p; multiple <= bound; multiple += p * 2) {
					composite[static_cast<std::size_t>((multiple - 3) / 2)] = true;
				}
			}
		}

		u64 count = 1; // 2 is handled outside the odd-only table.
		for (std::size_t index = 0; index < composite.size(); ++index) {
			if (!composite[index]) {
				if (count == n) {
					return static_cast<u64>(index) * 2 + 3;
				}
				++count;
			}
		}

		bound *= 2;
	}
}

static std::vector<std::uint32_t> simple_primes_up_to(u64 limit) {
	std::vector<bool> composite(limit + 1, false);
	for (u64 p = 2; p <= limit / p; ++p) {
		if (!composite[p]) {
			for (u64 multiple = p * p; multiple <= limit; multiple += p) {
				composite[multiple] = true;
			}
		}
	}
	std::vector<std::uint32_t> primes;
	for (u64 candidate = 2; candidate <= limit; ++candidate) {
		if (!composite[candidate]) {
			primes.push_back(static_cast<std::uint32_t>(candidate));
		}
	}
	return primes;
}

static u64 nth_prime_segmented(u64 n, u64 segment_width = 1 << 20) {
	if (n == 0) {
		return 2;
	}

	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(bound))) + 1;
		const auto base_primes = simple_primes_up_to(root);
		u64 count = 0;

		for (u64 low = 2; low <= bound; low += segment_width) {
			const u64 high = std::min(bound + 1, low + segment_width);
			std::vector<bool> composite(high - low, false);

			for (const u64 p : base_primes) {
				const u64 square = p * p;
				if (square >= high) {
					break;
				}
				u64 start = square > low ? square : ((low + p - 1) / p) * p;
				for (u64 multiple = start; multiple < high; multiple += p) {
					composite[multiple - low] = true;
				}
			}

			for (u64 candidate = low; candidate < high; ++candidate) {
				if (candidate >= 2 && !composite[candidate - low]) {
					if (count == n) {
						return candidate;
					}
					++count;
				}
			}
		}

		bound *= 2;
	}
}

static u64 nth_prime_segmented_odd(u64 n, u64 segment_odds = 1 << 19) {
	if (n == 0) {
		return 2;
	}

	const u64 segment_width = segment_odds * 2;
	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(bound))) + 1;
		const auto base_primes = simple_primes_up_to(root);
		u64 count = 1; // 2 is handled outside the odd-only segments.

		for (u64 low = 3; low <= bound; low += segment_width) {
			const u64 high = std::min(bound + 1, low + segment_width);
			const auto odd_count = static_cast<std::size_t>((high - low + 1) / 2);
			std::vector<std::uint8_t> composite(odd_count, 0);

			for (const u64 p : base_primes) {
				if (p == 2) {
					continue;
				}
				const u64 square = p * p;
				if (square >= high) {
					break;
				}
				u64 start = square > low ? square : ((low + p - 1) / p) * p;
				if ((start & 1) == 0) {
					start += p;
				}
				for (u64 multiple = start; multiple < high; multiple += p * 2) {
					composite[static_cast<std::size_t>((multiple - low) / 2)] = 1;
				}
			}

			for (std::size_t index = 0; index < composite.size(); ++index) {
				const u64 candidate = low + static_cast<u64>(index) * 2;
				if (candidate > bound) {
					break;
				}
				if (composite[index] == 0) {
					if (count == n) {
						return candidate;
					}
					++count;
				}
			}
		}

		bound *= 2;
	}
}

static bool is_wheel30_residue(u64 x) {
	switch (x % 30) {
		case 1:
		case 7:
		case 11:
		case 13:
		case 17:
		case 19:
		case 23:
		case 29:
			return true;
		default:
			return false;
	}
}

static constexpr u64 wheel30_residues[] = {1, 7, 11, 13, 17, 19, 23, 29};
static constexpr u64 wheel30_deltas[] = {6, 4, 2, 4, 2, 4, 6, 2};

static u64 first_wheel30_candidate_at_least(u64 value) {
	if (value <= 1) {
		return 1;
	}
	const u64 base = (value / 30) * 30;
	for (const u64 residue : wheel30_residues) {
		const u64 candidate = base + residue;
		if (candidate >= value) {
			return candidate;
		}
	}
	return base + 31;
}

static std::size_t wheel30_residue_index(u64 value) {
	switch (value % 30) {
		case 1:
			return 0;
		case 7:
			return 1;
		case 11:
			return 2;
		case 13:
			return 3;
		case 17:
			return 4;
		case 19:
			return 5;
		case 23:
			return 6;
		case 29:
			return 7;
		default:
			throw std::logic_error("value is not a wheel-30 candidate");
	}
}

static std::size_t wheel30_index(u64 value, u64 segment_base) {
	const u64 offset = value - segment_base;
	return static_cast<std::size_t>((offset / 30) * 8 + wheel30_residue_index(value));
}

static std::uint8_t wheel30_bit(u64 value) {
	return static_cast<std::uint8_t>(1u << wheel30_residue_index(value));
}

static unsigned wheel30_survivor_count(std::uint8_t composite) {
	return std::popcount(static_cast<unsigned>(~composite & 0xffu));
}

static u64 nth_prime_wheel30_segmented(u64 n, u64 segment_width = 1 << 20) {
	if (n < 3) {
		return small_primes[n];
	}

	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(bound))) + 1;
		const auto base_primes = simple_primes_up_to(root);
		u64 count = 3; // 2, 3, 5 are handled by the wheel bootstrap.

		for (u64 low = 7; low <= bound; low += segment_width) {
			const u64 high = std::min(bound + 1, low + segment_width);
			std::vector<bool> composite(high - low, false);

			for (const u64 p : base_primes) {
				if (p <= 5) {
					continue;
				}
				const u64 square = p * p;
				if (square >= high) {
					break;
				}
				u64 start = square > low ? square : ((low + p - 1) / p) * p;
				for (u64 multiple = start; multiple < high; multiple += p) {
					composite[multiple - low] = true;
				}
			}

			for (u64 candidate = low; candidate < high; ++candidate) {
				if (is_wheel30_residue(candidate) && !composite[candidate - low]) {
					if (count == n) {
						return candidate;
					}
					++count;
				}
			}
		}

		bound *= 2;
	}
}

static u64 nth_prime_wheel30_indexed(u64 n, u64 segment_periods = 1 << 15) {
	if (n < 3) {
		return small_primes[n];
	}

	const u64 segment_width = segment_periods * 30;
	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(bound))) + 1;
		const auto base_primes = simple_primes_up_to(root);
		u64 count = 3; // 2, 3, 5 are handled by the wheel bootstrap.

		for (u64 segment_base = 0; segment_base <= bound; segment_base += segment_width) {
			const u64 high = std::min(bound + 1, segment_base + segment_width);
			const u64 periods = (high - segment_base + 29) / 30;
			std::vector<std::uint8_t> composite(static_cast<std::size_t>(periods * 8), 0);

			for (const u64 p : base_primes) {
				if (p <= 5) {
					continue;
				}

				const u64 square = p * p;
				if (square >= high) {
					break;
				}

				const u64 start_value = std::max(square, segment_base);
				u64 multiplier = first_wheel30_candidate_at_least((start_value + p - 1) / p);
				std::size_t delta_index = wheel30_residue_index(multiplier);

				for (;;) {
					const u128 product = static_cast<u128>(p) * multiplier;
					if (product >= high) {
						break;
					}
					const u64 multiple = static_cast<u64>(product);
					if (multiple >= segment_base) {
						composite[wheel30_index(multiple, segment_base)] = 1;
					}
					multiplier += wheel30_deltas[delta_index];
					delta_index = (delta_index + 1) & 7;
				}
			}

			for (u64 period = 0; period < periods; ++period) {
				const u64 base = segment_base + period * 30;
				for (std::size_t residue_index = 0; residue_index < 8; ++residue_index) {
					const u64 candidate = base + wheel30_residues[residue_index];
					if (candidate < 7) {
						continue;
					}
					if (candidate > bound) {
						break;
					}
					if (!composite[static_cast<std::size_t>(period * 8 + residue_index)]) {
						if (count == n) {
							return candidate;
						}
						++count;
					}
				}
			}
		}

		bound *= 2;
	}
}

static u64 nth_prime_wheel30_bitset(u64 n, u64 segment_periods = 1 << 16) {
	if (n < 3) {
		return small_primes[n];
	}

	const u64 segment_width = segment_periods * 30;
	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(bound))) + 1;
		const auto base_primes = simple_primes_up_to(root);
		u64 count = 3; // 2, 3, 5 are handled by the wheel bootstrap.

		for (u64 segment_base = 0; segment_base <= bound; segment_base += segment_width) {
			const u64 high = std::min(bound + 1, segment_base + segment_width);
			const u64 periods = (high - segment_base + 29) / 30;
			std::vector<std::uint8_t> composite(static_cast<std::size_t>(periods), 0);

			for (const u64 p : base_primes) {
				if (p <= 5) {
					continue;
				}

				const u64 square = p * p;
				if (square >= high) {
					break;
				}

				const u64 start_value = std::max(square, segment_base);
				u64 multiplier = first_wheel30_candidate_at_least((start_value + p - 1) / p);
				std::size_t delta_index = wheel30_residue_index(multiplier);

				for (;;) {
					const u128 product = static_cast<u128>(p) * multiplier;
					if (product >= high) {
						break;
					}
					const u64 multiple = static_cast<u64>(product);
					if (multiple >= segment_base) {
						const std::size_t period = static_cast<std::size_t>((multiple - segment_base) / 30);
						composite[period] |= wheel30_bit(multiple);
					}
					multiplier += wheel30_deltas[delta_index];
					delta_index = (delta_index + 1) & 7;
				}
			}

			for (u64 period = 0; period < periods; ++period) {
				const u64 base = segment_base + period * 30;
				const bool edge_period = base < 7 || base + 29 > bound;

				if (!edge_period) {
					const unsigned survivors = std::popcount(static_cast<unsigned>(~composite[static_cast<std::size_t>(period)] & 0xffu));
					if (count + survivors <= n) {
						count += survivors;
						continue;
					}
				}

				for (std::size_t residue_index = 0; residue_index < 8; ++residue_index) {
					const u64 candidate = base + wheel30_residues[residue_index];
					if (candidate < 7) {
						continue;
					}
					if (candidate > bound) {
						break;
					}
					const auto bit = static_cast<std::uint8_t>(1u << residue_index);
					if ((composite[static_cast<std::size_t>(period)] & bit) == 0) {
						if (count == n) {
							return candidate;
						}
						++count;
					}
				}
			}
		}

		bound *= 2;
	}
}

struct WheelPrimeState {
	u64 p;
	u128 multiple;
	std::size_t delta_index;
};

struct WheelPrimeFsmState {
	u64 p;
	u64 multiple;
	std::uint32_t step[8];
	std::uint32_t period_advance[8];
	std::uint8_t mark_bit[8];
	std::uint8_t delta_index;
};

static WheelPrimeFsmState make_wheel30_fsm_state(u64 p, u64 start_value) {
	if (p > std::numeric_limits<std::uint32_t>::max() / 6) {
		throw std::overflow_error("wheel FSM step table exceeds 32-bit range");
	}
	WheelPrimeFsmState state{};
	state.p = p;

	u64 multiplier = first_wheel30_candidate_at_least((start_value + p - 1) / p);
	std::size_t delta_index = wheel30_residue_index(multiplier);
	u128 product = static_cast<u128>(p) * multiplier;
	while (product < start_value) {
		multiplier += wheel30_deltas[delta_index];
		delta_index = (delta_index + 1) & 7;
		product = static_cast<u128>(p) * multiplier;
	}

	state.multiple = static_cast<u64>(product);
	state.delta_index = static_cast<std::uint8_t>(delta_index);
	for (std::size_t i = 0; i < 8; ++i) {
		const u64 step = p * wheel30_deltas[i];
		const u64 residue = (p * wheel30_residues[i]) % 30;
		state.step[i] = static_cast<std::uint32_t>(step);
		state.period_advance[i] = static_cast<std::uint32_t>((residue + step) / 30);
		state.mark_bit[i] = static_cast<std::uint8_t>(1u << wheel30_residue_index(residue));
	}
	return state;
}

static std::vector<WheelPrimeFsmState> make_wheel30_fsm_states(
	const std::vector<std::uint32_t>& base_primes,
	u64 segment_base
) {
	std::vector<WheelPrimeFsmState> states;
	states.reserve(base_primes.size());
	for (const u64 p : base_primes) {
		if (p <= 5) {
			continue;
		}
		const u64 square = p * p;
		const u64 start_value = std::max(square, segment_base);
		states.push_back(make_wheel30_fsm_state(p, start_value));
	}
	return states;
}

static u64 nth_prime_wheel30_bitset_state(u64 n, u64 segment_periods = 1 << 16) {
	if (n < 3) {
		return small_primes[n];
	}

	const u64 segment_width = segment_periods * 30;
	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(bound))) + 1;
		const auto base_primes = simple_primes_up_to(root);
		std::vector<WheelPrimeState> states;
		states.reserve(base_primes.size());
		for (const u64 p : base_primes) {
			if (p > 5) {
				states.push_back(WheelPrimeState{
					p,
					static_cast<u128>(p) * p,
					wheel30_residue_index(p),
				});
			}
		}

		u64 count = 3; // 2, 3, 5 are handled by the wheel bootstrap.

		for (u64 segment_base = 0; segment_base <= bound; segment_base += segment_width) {
			const u64 high = std::min(bound + 1, segment_base + segment_width);
			const u64 periods = (high - segment_base + 29) / 30;
			std::vector<std::uint8_t> composite(static_cast<std::size_t>(periods), 0);

			for (auto& state : states) {
				if (state.multiple >= high) {
					break;
				}

				while (state.multiple < high) {
					const u64 multiple = static_cast<u64>(state.multiple);
					if (multiple >= segment_base) {
						const std::size_t period = static_cast<std::size_t>((multiple - segment_base) / 30);
						composite[period] |= wheel30_bit(multiple);
					}
					state.multiple += static_cast<u128>(state.p) * wheel30_deltas[state.delta_index];
					state.delta_index = (state.delta_index + 1) & 7;
				}
			}

			for (u64 period = 0; period < periods; ++period) {
				const u64 base = segment_base + period * 30;
				const bool edge_period = base < 7 || base + 29 > bound;

				if (!edge_period) {
					const unsigned survivors = std::popcount(static_cast<unsigned>(~composite[static_cast<std::size_t>(period)] & 0xffu));
					if (count + survivors <= n) {
						count += survivors;
						continue;
					}
				}

				for (std::size_t residue_index = 0; residue_index < 8; ++residue_index) {
					const u64 candidate = base + wheel30_residues[residue_index];
					if (candidate < 7) {
						continue;
					}
					if (candidate > bound) {
						break;
					}
					const auto bit = static_cast<std::uint8_t>(1u << residue_index);
					if ((composite[static_cast<std::size_t>(period)] & bit) == 0) {
						if (count == n) {
							return candidate;
						}
						++count;
					}
				}
			}
		}

		bound *= 2;
	}
}

static u64 nth_prime_wheel30_bitset_fsm(u64 n, u64 segment_periods = 1 << 16) {
	if (n < 3) {
		return small_primes[n];
	}

	const u64 segment_width = segment_periods * 30;
	u64 bound = upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(bound))) + 1;
		const auto base_primes = simple_primes_up_to(root);
		auto states = make_wheel30_fsm_states(base_primes, 0);

		u64 count = 3; // 2, 3, 5 are handled by the wheel bootstrap.

		for (u64 segment_base = 0; segment_base <= bound; segment_base += segment_width) {
			const u64 high = std::min(bound + 1, segment_base + segment_width);
			const u64 periods = (high - segment_base + 29) / 30;
			std::vector<std::uint8_t> composite(static_cast<std::size_t>(periods), 0);

			for (auto& state : states) {
				if (state.multiple >= high) {
					break;
				}

				std::size_t period = static_cast<std::size_t>((state.multiple - segment_base) / 30);
				while (state.multiple < high) {
					const std::size_t delta_index = state.delta_index;
					composite[period] |= state.mark_bit[delta_index];
					state.multiple += state.step[delta_index];
					period += state.period_advance[delta_index];
					state.delta_index = static_cast<std::uint8_t>((delta_index + 1) & 7);
				}
			}

			for (u64 period = 0; period < periods; ++period) {
				const u64 base = segment_base + period * 30;
				const bool edge_period = base < 7 || base + 29 > bound;

				if (!edge_period) {
					const unsigned survivors = std::popcount(static_cast<unsigned>(~composite[static_cast<std::size_t>(period)] & 0xffu));
					if (count + survivors <= n) {
						count += survivors;
						continue;
					}
				}

				for (std::size_t residue_index = 0; residue_index < 8; ++residue_index) {
					const u64 candidate = base + wheel30_residues[residue_index];
					if (candidate < 7) {
						continue;
					}
					if (candidate > bound) {
						break;
					}
					const auto bit = static_cast<std::uint8_t>(1u << residue_index);
					if ((composite[static_cast<std::size_t>(period)] & bit) == 0) {
						if (count == n) {
							return candidate;
						}
						++count;
					}
				}
			}
		}

		bound *= 2;
	}
}

struct PhiSmallCache {
	static constexpr std::size_t max_a = 6;
	static constexpr u64 period = 30030;

	u64 primorial[max_a + 1]{};
	u64 totient[max_a + 1]{};
	u64 table[max_a + 1][period]{};

	PhiSmallCache() {
		primorial[0] = 1;
		totient[0] = 1;
		for (std::size_t a = 1; a <= max_a; ++a) {
			const u64 p = small_primes[a - 1];
			primorial[a] = primorial[a - 1] * p;
			totient[a] = totient[a - 1] * (p - 1);
		}

		std::vector<std::uint8_t> survives(static_cast<std::size_t>(period), 1);
		survives[0] = 0;
		for (std::size_t a = 0; a <= max_a; ++a) {
			u64 running = 0;
			for (u64 x = 0; x < period; ++x) {
				running += survives[static_cast<std::size_t>(x)] != 0 ? 1 : 0;
				table[a][x] = running;
			}
			if (a < max_a) {
				const u64 p = small_primes[a];
				for (u64 multiple = p; multiple < period; multiple += p) {
					survives[static_cast<std::size_t>(multiple)] = 0;
				}
			}
		}
	}
};

static const PhiSmallCache& phi_small_cache() {
	static const PhiSmallCache cache;
	return cache;
}

static u64 phi_legendre(u64 x, std::size_t a, const std::vector<std::uint32_t>& primes) {
	if (x == 0) {
		return 0;
	}
	if (a == 0) {
		return x;
	}

	const auto& cache = phi_small_cache();
	if (a <= PhiSmallCache::max_a) {
		const u64 primorial = cache.primorial[a];
		return (x / primorial) * cache.totient[a] + cache.table[a][x % primorial];
	}
	if (a < primes.size() && x < primes[a]) {
		return 1;
	}

	u64 result = x;
	for (std::size_t i = 0; i < a; ++i) {
		const u64 q = x / primes[i];
		if (q == 0) {
			break;
		}
		const u64 removed = phi_legendre(q, i, primes);
		result -= removed;
		if (removed == 1) {
			for (std::size_t j = i + 1; j < a && primes[j] <= x; ++j) {
				--result;
			}
			return result;
		}
	}
	return result;
}

static u64 prime_count_legendre(u64 x, const std::vector<std::uint32_t>& primes) {
	if (x < 2) {
		return 0;
	}
	const u64 root = isqrt_floor(x);
	const auto end = std::upper_bound(primes.begin(), primes.end(), root);
	const auto a = static_cast<std::size_t>(end - primes.begin());
	return phi_legendre(x, a, primes) + static_cast<u64>(a) - 1;
}

static u64 prime_count_lehmer_rec(
	u64 x,
	const std::vector<std::uint32_t>& primes,
	const std::vector<std::uint32_t>& pi_lookup,
	std::unordered_map<u64, u64>& cache
) {
	if (x < 2) {
		return 0;
	}
	if (x < pi_lookup.size()) {
		return pi_lookup[static_cast<std::size_t>(x)];
	}
	if (!primes.empty() && x <= primes.back()) {
		return static_cast<u64>(std::upper_bound(primes.begin(), primes.end(), x) - primes.begin());
	}

	const auto cached = cache.find(x);
	if (cached != cache.end()) {
		return cached->second;
	}

	const u64 x_quarter = isqrt_floor(isqrt_floor(x));
	const u64 x_sqrt = isqrt_floor(x);
	const u64 x_cbrt = icbrt_floor(x);
	const u64 a = prime_count_lehmer_rec(x_quarter, primes, pi_lookup, cache);
	const u64 b = prime_count_lehmer_rec(x_sqrt, primes, pi_lookup, cache);
	const u64 c = prime_count_lehmer_rec(x_cbrt, primes, pi_lookup, cache);

	u64 result = phi_legendre(x, static_cast<std::size_t>(a), primes);
	result += ((b + a - 2) * (b - a + 1)) / 2;

	for (u64 i = a; i < b; ++i) {
		const u64 w = x / primes[static_cast<std::size_t>(i)];
		result -= prime_count_lehmer_rec(w, primes, pi_lookup, cache);
		if (i < c) {
			const u64 limit = prime_count_lehmer_rec(isqrt_floor(w), primes, pi_lookup, cache);
			for (u64 j = i; j < limit; ++j) {
				result -= prime_count_lehmer_rec(w / primes[static_cast<std::size_t>(j)], primes, pi_lookup, cache) - j;
			}
		}
	}

	cache.emplace(x, result);
	return result;
}

struct PhiMediumCache {
	static constexpr std::size_t max_a = 7;
	static constexpr u64 period = 510510;

	u64 primorial[max_a + 1]{};
	u64 totient[max_a + 1]{};
	u64 table[max_a + 1][period]{};

	PhiMediumCache() {
		primorial[0] = 1;
		totient[0] = 1;
		for (std::size_t a = 1; a <= max_a; ++a) {
			const u64 p = small_primes[a - 1];
			primorial[a] = primorial[a - 1] * p;
			totient[a] = totient[a - 1] * (p - 1);
		}

		std::vector<std::uint8_t> survives(static_cast<std::size_t>(period), 1);
		survives[0] = 0;
		for (std::size_t a = 0; a <= max_a; ++a) {
			u64 running = 0;
			for (u64 x = 0; x < period; ++x) {
				running += survives[static_cast<std::size_t>(x)] != 0 ? 1 : 0;
				table[a][x] = running;
			}
			if (a < max_a) {
				const u64 p = small_primes[a];
				for (u64 multiple = p; multiple < period; multiple += p) {
					survives[static_cast<std::size_t>(multiple)] = 0;
				}
			}
		}
	}
};

static const PhiMediumCache& phi_medium_cache() {
	static const PhiMediumCache cache;
	return cache;
}

static u64 phi_legendre_medium(u64 x, std::size_t a, const std::vector<std::uint32_t>& primes) {
	if (x == 0) {
		return 0;
	}
	if (a == 0) {
		return x;
	}

	const auto& cache = phi_medium_cache();
	if (a <= PhiMediumCache::max_a) {
		const u64 primorial = cache.primorial[a];
		return (x / primorial) * cache.totient[a] + cache.table[a][x % primorial];
	}
	if (a < primes.size() && x < primes[a]) {
		return 1;
	}

	u64 result = x;
	for (std::size_t i = 0; i < a; ++i) {
		const u64 q = x / primes[i];
		if (q == 0) {
			break;
		}
		const u64 removed = phi_legendre_medium(q, i, primes);
		result -= removed;
		if (removed == 1) {
			for (std::size_t j = i + 1; j < a && primes[j] <= x; ++j) {
				--result;
			}
			return result;
		}
	}
	return result;
}

static u64 prime_count_lehmer_phi7_rec(
	u64 x,
	const std::vector<std::uint32_t>& primes,
	const std::vector<std::uint32_t>& pi_lookup,
	std::unordered_map<u64, u64>& cache
) {
	if (x < 2) {
		return 0;
	}
	if (x < pi_lookup.size()) {
		return pi_lookup[static_cast<std::size_t>(x)];
	}
	if (!primes.empty() && x <= primes.back()) {
		return static_cast<u64>(std::upper_bound(primes.begin(), primes.end(), x) - primes.begin());
	}

	const auto cached = cache.find(x);
	if (cached != cache.end()) {
		return cached->second;
	}

	const u64 x_quarter = isqrt_floor(isqrt_floor(x));
	const u64 x_sqrt = isqrt_floor(x);
	const u64 x_cbrt = icbrt_floor(x);
	const u64 a = prime_count_lehmer_phi7_rec(x_quarter, primes, pi_lookup, cache);
	const u64 b = prime_count_lehmer_phi7_rec(x_sqrt, primes, pi_lookup, cache);
	const u64 c = prime_count_lehmer_phi7_rec(x_cbrt, primes, pi_lookup, cache);

	u64 result = phi_legendre_medium(x, static_cast<std::size_t>(a), primes);
	result += ((b + a - 2) * (b - a + 1)) / 2;

	for (u64 i = a; i < b; ++i) {
		const u64 w = x / primes[static_cast<std::size_t>(i)];
		result -= prime_count_lehmer_phi7_rec(w, primes, pi_lookup, cache);
		if (i < c) {
			const u64 limit = prime_count_lehmer_phi7_rec(isqrt_floor(w), primes, pi_lookup, cache);
			for (u64 j = i; j < limit; ++j) {
				result -= prime_count_lehmer_phi7_rec(w / primes[static_cast<std::size_t>(j)], primes, pi_lookup, cache) - j;
			}
		}
	}

	cache.emplace(x, result);
	return result;
}

static std::vector<std::uint32_t> make_prime_pi_lookup(const std::vector<std::uint32_t>& primes) {
	if (primes.empty()) {
		return {};
	}
	const std::size_t limit = static_cast<std::size_t>(primes.back());
	std::vector<std::uint32_t> lookup(limit + 1, 0);
	std::uint32_t count = 0;
	std::size_t prime_index = 0;
	for (std::size_t value = 0; value <= limit; ++value) {
		if (prime_index < primes.size() && primes[prime_index] == value) {
			++count;
			++prime_index;
		}
		lookup[value] = count;
	}
	return lookup;
}

static u64 lagrange_skip_base_from_lower(u64 lower, u64 segment_width, u64 bound) {
	if (lower <= segment_width * 2 || lower >= bound) {
		return 0;
	}
	lower = (lower / segment_width) * segment_width;
	if (lower > segment_width) {
		lower -= segment_width;
	}
	return lower;
}

enum class SkipStrategy {
	dusart_lower,
	approximate_tight,
};

enum class BoundStrategy {
	classic,
	axler,
};

template <typename PrimeCounter>
static u64 find_skip_base_from_estimate(
	u64 n,
	u64 segment_width,
	u64 bound,
	u64 estimate,
	const PrimeCounter& prime_count
) {
	if (estimate <= segment_width * 2 || estimate >= bound) {
		return 0;
	}

	u64 segment_base = (estimate / segment_width) * segment_width;
	if (segment_base > segment_width) {
		segment_base -= segment_width;
	}

	for (;;) {
		const u64 count = prime_count(segment_base - 1);
		if (count <= n || segment_base == 0) {
			return segment_base;
		}
		if (segment_base <= segment_width) {
			return 0;
		}
		segment_base -= segment_width;
	}
}

static u64 nth_prime_lagrange_fsm_impl(
	u64 n,
	u64 segment_periods,
	bool use_lehmer_count,
	SkipStrategy skip_strategy,
	BoundStrategy bound_strategy = BoundStrategy::classic,
	bool use_phi7_count = false
) {
	if (n < 3) {
		return small_primes[n];
	}

	const u64 segment_width = segment_periods * 30;
	u64 bound = bound_strategy == BoundStrategy::axler
		? axler_upper_bound_for_nth_prime(n)
		: upper_bound_for_nth_prime(n);
	for (;;) {
		const u64 root = isqrt_floor(bound) + 1;
		const auto base_primes = simple_primes_up_to(root);
		const auto pi_lookup = use_lehmer_count ? make_prime_pi_lookup(base_primes) : std::vector<std::uint32_t>{};
		std::unordered_map<u64, u64> lehmer_cache;
		if (use_lehmer_count) {
			lehmer_cache.reserve(4096);
		}
		const auto prime_count = [&](u64 x) {
			if (!use_lehmer_count) {
				return prime_count_legendre(x, base_primes);
			}
			return use_phi7_count
				? prime_count_lehmer_phi7_rec(x, base_primes, pi_lookup, lehmer_cache)
				: prime_count_lehmer_rec(x, base_primes, pi_lookup, lehmer_cache);
		};
		const u64 lower_bound = bound_strategy == BoundStrategy::axler
			? axler_lower_bound_for_nth_prime(n)
			: lower_bound_for_nth_prime(n);
		u64 segment_base = skip_strategy == SkipStrategy::approximate_tight
			? find_skip_base_from_estimate(n, segment_width, bound, approximate_nth_prime(n), prime_count)
			: lagrange_skip_base_from_lower(
				lower_bound,
				segment_width,
				bound
			);
		u64 count = 3;

		if (segment_base > 0) {
			for (;;) {
				count = prime_count(segment_base - 1);
				if (count <= n || segment_base == 0) {
					break;
				}
				if (segment_base <= segment_width) {
					segment_base = 0;
					count = 3;
					break;
				}
				segment_base -= segment_width;
			}
		}

		auto states = make_wheel30_fsm_states(base_primes, segment_base);
		std::vector<std::uint8_t> composite(static_cast<std::size_t>(segment_periods), 0);

		for (; segment_base <= bound; segment_base += segment_width) {
			const u64 high = std::min(bound + 1, segment_base + segment_width);
			const u64 periods = (high - segment_base + 29) / 30;
			std::fill(composite.begin(), composite.begin() + static_cast<std::ptrdiff_t>(periods), 0);

			for (auto& state : states) {
				if (state.multiple >= high) {
					if (state.p > high / state.p) {
						break;
					}
					continue;
				}

				std::size_t period = static_cast<std::size_t>((state.multiple - segment_base) / 30);
				while (state.multiple < high) {
					const std::size_t delta_index = state.delta_index;
					composite[period] |= state.mark_bit[delta_index];
					state.multiple += state.step[delta_index];
					period += state.period_advance[delta_index];
					state.delta_index = static_cast<std::uint8_t>((delta_index + 1) & 7);
				}
			}

			for (u64 period = 0; period < periods; ++period) {
				const u64 base = segment_base + period * 30;
				const bool edge_period = base < 7 || base + 29 > bound;

				if (!edge_period) {
					const unsigned survivors = wheel30_survivor_count(composite[static_cast<std::size_t>(period)]);
					if (count + survivors <= n) {
						count += survivors;
						continue;
					}
				}

				for (std::size_t residue_index = 0; residue_index < 8; ++residue_index) {
					const u64 candidate = base + wheel30_residues[residue_index];
					if (candidate < 7) {
						continue;
					}
					if (candidate > bound) {
						break;
					}
					const auto bit = static_cast<std::uint8_t>(1u << residue_index);
					if ((composite[static_cast<std::size_t>(period)] & bit) == 0) {
						if (count == n) {
							return candidate;
						}
						++count;
					}
				}
			}
		}

		bound *= 2;
	}
}

static u64 nth_prime_lagrange_fsm(u64 n, u64 segment_periods = 1 << 16) {
	return nth_prime_lagrange_fsm_impl(n, segment_periods, false, SkipStrategy::dusart_lower);
}

static u64 nth_prime_lagrange_lehmer_fsm(u64 n, u64 segment_periods = 1 << 16) {
	return nth_prime_lagrange_fsm_impl(n, segment_periods, true, SkipStrategy::dusart_lower);
}

static u64 nth_prime_lagrange_lehmer_tight_fsm(u64 n, u64 segment_periods = 1 << 16) {
	return nth_prime_lagrange_fsm_impl(n, segment_periods, true, SkipStrategy::approximate_tight);
}

static u64 nth_prime_lagrange_lehmer_fsm_s17(u64 n) {
	return nth_prime_lagrange_fsm_impl(n, 1 << 17, true, SkipStrategy::dusart_lower);
}

static u64 nth_prime_lagrange_lehmer_fsm_s18(u64 n) {
	return nth_prime_lagrange_fsm_impl(n, 1 << 18, true, SkipStrategy::dusart_lower);
}

static u64 nth_prime_lagrange_lehmer_fsm_s19(u64 n) {
	return nth_prime_lagrange_fsm_impl(n, 1 << 19, true, SkipStrategy::dusart_lower);
}

static u64 nth_prime_lagrange_lehmer_axler_fsm(u64 n) {
	return nth_prime_lagrange_fsm_impl(n, 1 << 16, true, SkipStrategy::dusart_lower, BoundStrategy::axler);
}

static u64 nth_prime_lagrange_lehmer_axler_phi7_fsm(u64 n) {
	return nth_prime_lagrange_fsm_impl(n, 1 << 16, true, SkipStrategy::dusart_lower, BoundStrategy::axler, true);
}

static void print_usage(const char* exe) {
	std::cerr << "Usage: " << exe << " <algorithm> <zero-indexed-n> [--time]\n"
	          << "\nPrimary algorithms:\n"
	          << "  naive-iterate\n"
	          << "  sqrt-iterate\n"
	          << "  miller-rabin-iterate\n"
	          << "  sieve-erat\n"
	          << "  sieve-erat-odd\n"
	          << "  sieve-erat-segm\n"
	          << "  sieve-erat-segm-odd\n"
	          << "  sieve-wheel30-segm\n"
	          << "  sieve-wheel30-indexed\n"
	          << "  sieve-wheel30-bitset\n"
	          << "  sieve-wheel30-bitset-state\n"
	          << "  sieve-wheel30-bitset-fsm\n"
	          << "  sieve-lagrange-fsm\n"
	          << "  sieve-lagrange-lehmer-fsm\n"
	          << "  sieve-lagrange-lehmer-axler-fsm\n"
	          << "  sieve-lagrange-lehmer-axler-phi7-fsm\n"
	          << "\nExperimental tuning variants (verified, not included in headline graphs):\n"
	          << "  sieve-lagrange-lehmer-tight-fsm\n"
	          << "  sieve-lagrange-lehmer-fsm-s17\n"
	          << "  sieve-lagrange-lehmer-fsm-s18\n"
	          << "  sieve-lagrange-lehmer-fsm-s19\n";
}

int main(int argc, char** argv) {
	if (argc < 3 || argc > 4) {
		print_usage(argv[0]);
		return 2;
	}

	const std::string_view algorithm = argv[1];
	const u64 n = parse_u64(argv[2]);
	const bool show_time = argc == 4 && std::string_view(argv[3]) == "--time";

	const auto start = std::chrono::steady_clock::now();
	u64 prime = 0;

	if (algorithm == "naive-iterate") {
		prime = nth_prime_by_iteration(n, is_prime_naive);
	} else if (algorithm == "sqrt-iterate") {
		prime = nth_prime_by_iteration(n, is_prime_sqrt);
	} else if (algorithm == "miller-rabin-iterate") {
		prime = nth_prime_by_iteration(n, is_prime_miller_rabin);
	} else if (algorithm == "sieve-erat") {
		prime = nth_prime_sieve_erat(n);
	} else if (algorithm == "sieve-erat-odd") {
		prime = nth_prime_sieve_erat_odd(n);
	} else if (algorithm == "sieve-erat-segm") {
		prime = nth_prime_segmented(n);
	} else if (algorithm == "sieve-erat-segm-odd") {
		prime = nth_prime_segmented_odd(n);
	} else if (algorithm == "sieve-wheel30-segm") {
		prime = nth_prime_wheel30_segmented(n);
	} else if (algorithm == "sieve-wheel30-indexed") {
		prime = nth_prime_wheel30_indexed(n);
	} else if (algorithm == "sieve-wheel30-bitset") {
		prime = nth_prime_wheel30_bitset(n);
	} else if (algorithm == "sieve-wheel30-bitset-state") {
		prime = nth_prime_wheel30_bitset_state(n);
	} else if (algorithm == "sieve-wheel30-bitset-fsm") {
		prime = nth_prime_wheel30_bitset_fsm(n);
	} else if (algorithm == "sieve-lagrange-fsm") {
		prime = nth_prime_lagrange_fsm(n);
	} else if (algorithm == "sieve-lagrange-lehmer-fsm") {
		prime = nth_prime_lagrange_lehmer_fsm(n);
	} else if (algorithm == "sieve-lagrange-lehmer-tight-fsm") {
		prime = nth_prime_lagrange_lehmer_tight_fsm(n);
	} else if (algorithm == "sieve-lagrange-lehmer-fsm-s17") {
		prime = nth_prime_lagrange_lehmer_fsm_s17(n);
	} else if (algorithm == "sieve-lagrange-lehmer-fsm-s18") {
		prime = nth_prime_lagrange_lehmer_fsm_s18(n);
	} else if (algorithm == "sieve-lagrange-lehmer-fsm-s19") {
		prime = nth_prime_lagrange_lehmer_fsm_s19(n);
	} else if (algorithm == "sieve-lagrange-lehmer-axler-fsm") {
		prime = nth_prime_lagrange_lehmer_axler_fsm(n);
	} else if (algorithm == "sieve-lagrange-lehmer-axler-phi7-fsm") {
		prime = nth_prime_lagrange_lehmer_axler_phi7_fsm(n);
	} else {
		throw std::invalid_argument("unknown algorithm");
	}

	const auto end = std::chrono::steady_clock::now();
	const auto elapsed = std::chrono::duration<double>(end - start).count();

	std::cout << prime << "\n";
	if (show_time) {
		std::cerr << elapsed << "\n";
	}

	return 0;
}
