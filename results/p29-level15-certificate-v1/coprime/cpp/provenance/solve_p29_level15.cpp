#include <algorithm>
#include <array>
#include <charconv>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace {

constexpr int kCoordinates = 14;
constexpr int kChoices = 15;
constexpr int kPrime = 29;
constexpr int kLevel = 15;
constexpr int kModulus = kPrime * kLevel;
constexpr int kTimes = kModulus / 2;
constexpr std::uint16_t kAllChoices = (1U << kChoices) - 1U;
constexpr const char* kSolverVersion = "1.1.0";

using Domains = std::array<std::uint16_t, kCoordinates>;

int popcount(std::uint16_t value) {
    return __builtin_popcount(static_cast<unsigned int>(value));
}

int first_choice(std::uint16_t value) {
    return __builtin_ctz(static_cast<unsigned int>(value));
}

int speed(int coordinate, int choice) {
    return coordinate + 1 + kPrime * choice;
}

int distance_mod(int value) {
    int residue = value % kModulus;
    return std::min(residue, kModulus - residue);
}

bool parse_integer(const std::string& text, int& result) {
    if (text.empty()) {
        return false;
    }
    const char* begin = text.data();
    const char* end = begin + text.size();
    auto parsed = std::from_chars(begin, end, result);
    return parsed.ec == std::errc() && parsed.ptr == end;
}

class Solver {
public:
    Solver(
        std::string symmetry_case,
        std::vector<std::pair<int, int>> fixed_choices,
        bool require_gcd_failure
    )
        : symmetry_case_(std::move(symmetry_case)),
          fixed_choices_(std::move(fixed_choices)),
          require_gcd_failure_(require_gcd_failure) {
        build_masks();
    }

    bool solve() {
        Domains domains;
        domains.fill(kAllChoices);

        if (symmetry_case_ == "coprime") {
            domains[0] = 1U;
        } else if (symmetry_case_ == "noncoprime") {
            for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
                domains[coordinate] &= noncoprime_masks_[coordinate];
            }
            domains[2] = 1U;
        }

        for (const auto& [coordinate, choice] : fixed_choices_) {
            domains[coordinate - 1] &= static_cast<std::uint16_t>(
                1U << choice
            );
            if (domains[coordinate - 1] == 0) {
                return false;
            }
        }

        return search(domains);
    }

    bool internal_error() const {
        return internal_error_;
    }

    void print_result(bool satisfiable) const {
        std::cout << "case " << symmetry_case_ << "\n";
        std::cout << "constraint_mode "
                  << (
                      require_gcd_failure_
                          ? "improperness"
                          : "time-cover-only"
                  )
                  << "\n";
        std::cout << "status ";
        if (internal_error_) {
            std::cout << "ERROR\n";
        } else {
            std::cout << (satisfiable ? "SAT" : "UNSAT") << "\n";
        }
        std::cout << "nodes " << nodes_ << "\n";
        std::cout << "propagations " << propagations_ << "\n";
        std::cout << "domain_branches " << domain_branches_ << "\n";
        for (const auto& [coordinate, choice] : fixed_choices_) {
            std::cout << "fixed " << coordinate << ":" << choice << "\n";
        }
        if (satisfiable) {
            std::cout << "choices";
            for (int choice : solution_choices_) {
                std::cout << " " << choice;
            }
            std::cout << "\n";
            std::cout << "speeds";
            for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
                std::cout << " "
                          << speed(coordinate, solution_choices_[coordinate]);
            }
            std::cout << "\n";
        }
    }

private:
    void build_masks() {
        for (int time = 1; time <= kTimes; ++time) {
            for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
                std::uint16_t mask = 0;
                for (int choice = 0; choice < kChoices; ++choice) {
                    if (
                        kChoices * distance_mod(
                            time * speed(coordinate, choice)
                        ) < kModulus
                    ) {
                        mask |= static_cast<std::uint16_t>(1U << choice);
                    }
                }
                bad_masks_[time - 1][coordinate] = mask;
            }
        }

        for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
            std::uint16_t nondivisible_by_three = 0;
            std::uint16_t nondivisible_by_five = 0;
            std::uint16_t noncoprime = 0;
            for (int choice = 0; choice < kChoices; ++choice) {
                int value = speed(coordinate, choice);
                if (value % 3 != 0) {
                    nondivisible_by_three |=
                        static_cast<std::uint16_t>(1U << choice);
                }
                if (value % 5 != 0) {
                    nondivisible_by_five |=
                        static_cast<std::uint16_t>(1U << choice);
                }
                if (std::gcd(value, kLevel) > 1) {
                    noncoprime |=
                        static_cast<std::uint16_t>(1U << choice);
                }
            }
            nondivisible_masks_[0][coordinate] = nondivisible_by_three;
            nondivisible_masks_[1][coordinate] = nondivisible_by_five;
            noncoprime_masks_[coordinate] = noncoprime;
        }
    }

    bool propagate_cardinality(
        Domains& domains,
        const std::array<std::uint16_t, kCoordinates>& qualifying
    ) {
        int guaranteed = 0;
        std::vector<int> optional;
        for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
            std::uint16_t allowed = domains[coordinate];
            std::uint16_t qualifying_allowed =
                static_cast<std::uint16_t>(allowed & qualifying[coordinate]);
            if (qualifying_allowed == 0) {
                continue;
            }
            if (qualifying_allowed == allowed) {
                ++guaranteed;
            } else {
                optional.push_back(coordinate);
            }
        }

        if (guaranteed >= 2) {
            return true;
        }
        if (guaranteed + static_cast<int>(optional.size()) < 2) {
            return false;
        }
        if (guaranteed + static_cast<int>(optional.size()) == 2) {
            for (int coordinate : optional) {
                domains[coordinate] &= qualifying[coordinate];
                if (domains[coordinate] == 0) {
                    return false;
                }
            }
        }
        return true;
    }

    bool propagate(Domains& domains) {
        bool changed;
        do {
            ++propagations_;
            Domains before = domains;

            if (require_gcd_failure_) {
                if (
                    !propagate_cardinality(domains, nondivisible_masks_[0])
                    || !propagate_cardinality(domains, nondivisible_masks_[1])
                ) {
                    return false;
                }
            }

            for (int time = 0; time < kTimes; ++time) {
                bool guaranteed = false;
                int candidate_coordinate = -1;
                int candidate_coordinates = 0;

                for (
                    int coordinate = 0;
                    coordinate < kCoordinates;
                    ++coordinate
                ) {
                    std::uint16_t allowed = domains[coordinate];
                    std::uint16_t covering = static_cast<std::uint16_t>(
                        allowed & bad_masks_[time][coordinate]
                    );
                    if (covering == allowed) {
                        guaranteed = true;
                        break;
                    }
                    if (covering != 0) {
                        candidate_coordinate = coordinate;
                        ++candidate_coordinates;
                    }
                }

                if (guaranteed) {
                    continue;
                }
                if (candidate_coordinates == 0) {
                    return false;
                }
                if (candidate_coordinates == 1) {
                    domains[candidate_coordinate] &=
                        bad_masks_[time][candidate_coordinate];
                    if (domains[candidate_coordinate] == 0) {
                        return false;
                    }
                }
            }

            changed = domains != before;
        } while (changed);
        return true;
    }

    bool all_constraints_guaranteed(const Domains& domains) const {
        for (int time = 0; time < kTimes; ++time) {
            bool guaranteed = false;
            for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
                std::uint16_t allowed = domains[coordinate];
                if (
                    (allowed & bad_masks_[time][coordinate]) == allowed
                ) {
                    guaranteed = true;
                    break;
                }
            }
            if (!guaranteed) {
                return false;
            }
        }

        if (require_gcd_failure_) {
            for (const auto& qualifying : nondivisible_masks_) {
                int guaranteed = 0;
                for (
                    int coordinate = 0;
                    coordinate < kCoordinates;
                    ++coordinate
                ) {
                    std::uint16_t allowed = domains[coordinate];
                    if ((allowed & qualifying[coordinate]) == allowed) {
                        ++guaranteed;
                    }
                }
                if (guaranteed < 2) {
                    return false;
                }
            }
        }
        return true;
    }

    bool record_solution(const Domains& domains) {
        for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
            solution_choices_[coordinate] =
                first_choice(domains[coordinate]);
        }
        return validate_solution();
    }

    bool validate_solution() const {
        int nondivisible_by_three = 0;
        int nondivisible_by_five = 0;
        for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
            int value = speed(coordinate, solution_choices_[coordinate]);
            nondivisible_by_three += value % 3 != 0;
            nondivisible_by_five += value % 5 != 0;
        }
        if (
            require_gcd_failure_
            && (
                nondivisible_by_three < 2
                || nondivisible_by_five < 2
            )
        ) {
            return false;
        }

        for (int time = 1; time <= kTimes; ++time) {
            bool covered = false;
            for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
                int value = speed(
                    coordinate,
                    solution_choices_[coordinate]
                );
                if (
                    kChoices * distance_mod(time * value) < kModulus
                ) {
                    covered = true;
                    break;
                }
            }
            if (!covered) {
                return false;
            }
        }
        return true;
    }

    int select_branch_time(
        const Domains& domains,
        std::vector<int>& coordinates
    ) const {
        int best_time = -1;
        int best_variables = kCoordinates + 1;
        int best_literals = kCoordinates * kChoices + 1;

        for (int time = 0; time < kTimes; ++time) {
            bool guaranteed = false;
            int variables = 0;
            int literals = 0;
            for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
                std::uint16_t allowed = domains[coordinate];
                std::uint16_t covering = static_cast<std::uint16_t>(
                    allowed & bad_masks_[time][coordinate]
                );
                if (covering == allowed) {
                    guaranteed = true;
                    break;
                }
                if (covering != 0) {
                    ++variables;
                    literals += popcount(covering);
                }
            }
            if (guaranteed) {
                continue;
            }
            if (
                variables < best_variables
                || (
                    variables == best_variables
                    && literals < best_literals
                )
            ) {
                best_time = time;
                best_variables = variables;
                best_literals = literals;
            }
        }

        coordinates.clear();
        if (best_time < 0) {
            return best_time;
        }
        for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
            if (
                domains[coordinate] & bad_masks_[best_time][coordinate]
            ) {
                coordinates.push_back(coordinate);
            }
        }
        std::sort(
            coordinates.begin(),
            coordinates.end(),
            [&](int left, int right) {
                int left_choices = popcount(
                    domains[left] & bad_masks_[best_time][left]
                );
                int right_choices = popcount(
                    domains[right] & bad_masks_[best_time][right]
                );
                return left_choices < right_choices;
            }
        );
        return best_time;
    }

    bool search(Domains domains) {
        if (internal_error_) {
            return false;
        }
        ++nodes_;
        if (nodes_ % 1000000 == 0) {
            std::cerr << "nodes " << nodes_ << "\n";
        }

        if (!propagate(domains)) {
            return false;
        }

        if (all_constraints_guaranteed(domains)) {
            bool valid = record_solution(domains);
            if (!valid) {
                internal_error_ = true;
            }
            return valid;
        }

        std::vector<int> coordinates;
        int time = select_branch_time(domains, coordinates);
        if (time < 0) {
            int branch_coordinate = -1;
            int branch_choices = kChoices + 1;
            for (int coordinate = 0; coordinate < kCoordinates; ++coordinate) {
                int choices = popcount(domains[coordinate]);
                if (choices > 1 && choices < branch_choices) {
                    branch_coordinate = coordinate;
                    branch_choices = choices;
                }
            }
            if (branch_coordinate < 0) {
                internal_error_ = true;
                return false;
            }
            ++domain_branches_;
            std::uint16_t choices = domains[branch_coordinate];
            while (choices != 0) {
                int choice = first_choice(choices);
                Domains branch = domains;
                branch[branch_coordinate] = static_cast<std::uint16_t>(
                    1U << choice
                );
                if (search(branch)) {
                    return true;
                }
                if (internal_error_) {
                    return false;
                }
                choices &= static_cast<std::uint16_t>(choices - 1U);
            }
            return false;
        }

        Domains remaining = domains;
        for (int coordinate : coordinates) {
            std::uint16_t covering = static_cast<std::uint16_t>(
                remaining[coordinate] & bad_masks_[time][coordinate]
            );
            if (covering == 0) {
                continue;
            }

            Domains branch = remaining;
            branch[coordinate] = covering;
            if (search(branch)) {
                return true;
            }
            if (internal_error_) {
                return false;
            }

            remaining[coordinate] &= static_cast<std::uint16_t>(
                ~bad_masks_[time][coordinate]
            );
            if (remaining[coordinate] == 0) {
                break;
            }
        }

        return false;
    }

    std::string symmetry_case_;
    std::vector<std::pair<int, int>> fixed_choices_;
    bool require_gcd_failure_;
    std::array<std::array<std::uint16_t, kCoordinates>, kTimes> bad_masks_{};
    std::array<
        std::array<std::uint16_t, kCoordinates>,
        2
    > nondivisible_masks_{};
    std::array<std::uint16_t, kCoordinates> noncoprime_masks_{};
    std::array<int, kCoordinates> solution_choices_{};
    std::uint64_t nodes_ = 0;
    std::uint64_t propagations_ = 0;
    std::uint64_t domain_branches_ = 0;
    bool internal_error_ = false;
};

}  // namespace

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--version") {
        std::cout << "solve_p29_level15 " << kSolverVersion << "\n";
        std::cout << "compiler " << __VERSION__ << "\n";
        std::cout << "cplusplus " << __cplusplus << "\n";
#ifdef NDEBUG
        std::cout << "assertions disabled\n";
#else
        std::cout << "assertions enabled\n";
#endif
        return 0;
    }
    if (argc < 2) {
        std::cerr
            << "usage: solve_p29_level15 "
            << "coprime|noncoprime|coprime-cover "
            << "[COORDINATE:CHOICE ...]\n";
        return 2;
    }
    std::string requested_case = argv[1];
    if (
        requested_case != "coprime"
        && requested_case != "noncoprime"
        && requested_case != "coprime-cover"
    ) {
        std::cerr << "unknown symmetry case: " << requested_case << "\n";
        return 2;
    }
    std::string symmetry_case = (
        requested_case == "coprime-cover"
            ? "coprime"
            : requested_case
    );
    bool require_gcd_failure = requested_case != "coprime-cover";

    std::array<int, kCoordinates> fixed_by_coordinate;
    fixed_by_coordinate.fill(-1);
    std::vector<std::pair<int, int>> fixed_choices;
    for (int index = 2; index < argc; ++index) {
        std::string value = argv[index];
        std::size_t separator = value.find(':');
        if (
            separator == std::string::npos
            || separator != value.rfind(':')
        ) {
            std::cerr << "invalid fixed choice: " << value << "\n";
            return 2;
        }
        int coordinate = 0;
        int choice = 0;
        if (
            !parse_integer(value.substr(0, separator), coordinate)
            || !parse_integer(value.substr(separator + 1), choice)
            || coordinate < 1
            || coordinate > kCoordinates
            || choice < 0
            || choice >= kChoices
        ) {
            std::cerr << "invalid fixed choice: " << value << "\n";
            return 2;
        }
        if (fixed_by_coordinate[coordinate - 1] != -1) {
            std::cerr << "duplicate fixed coordinate: " << coordinate << "\n";
            return 2;
        }
        fixed_by_coordinate[coordinate - 1] = choice;
        fixed_choices.emplace_back(coordinate, choice);
    }
    Solver solver(
        symmetry_case,
        fixed_choices,
        require_gcd_failure
    );
    bool satisfiable = solver.solve();
    solver.print_result(satisfiable);
    if (solver.internal_error()) {
        return 2;
    }
    return satisfiable ? 10 : 20;
}
