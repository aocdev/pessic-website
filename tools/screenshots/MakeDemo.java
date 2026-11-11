import cat.pessic.core.account.AccountOps;
import cat.pessic.core.budget.Category;
import cat.pessic.core.common.Money;
import cat.pessic.core.income.Income;
import cat.pessic.core.income.IncomeOps;
import cat.pessic.core.profile.Profile;
import cat.pessic.core.savings.Pot;
import cat.pessic.core.savings.PotEntry;
import cat.pessic.core.savings.SavingsOps;
import cat.pessic.db.Database;
import cat.pessic.db.backup.BackupImporter;
import cat.pessic.db.profile.ProfileRepository;
import java.io.FileInputStream;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.YearMonth;

/** Demo database for the website screenshots: the invented profile "Marta" from the test sample. */
public class MakeDemo {
    public static void main(String[] a) throws Exception {
        try (var db = Database.open(Path.of(a[1])); var in = new FileInputStream(a[0])) {
            var repo = new ProfileRepository(db);
            new BackupImporter().importInto(in, repo);
            Profile p = repo.find("marta").orElseThrow();
            LocalDate oct1 = LocalDate.of(2026, 10, 1);
            p = SavingsOps.setReserveBalance(p, Money.of("640"), oct1);
            Pot trip = Pot.newGoal("Viatge a Itàlia", Money.of("1500"), YearMonth.of(2027, 6), Money.of("120"), Money.of("480"), oct1);
            Pot emergency = Pot.newGoal("Fons d'emergència", Money.of("6000"), null, Money.of("100"), Money.of("2900"), oct1);
            p = SavingsOps.saveGoal(SavingsOps.saveGoal(p, trip), emergency);
            // two earlier months, paid and closed, so the history has something to show
            String[][] sep = {{"2026-08-30", "Súper", "01", "62.40"}, {"2026-09-02", "Benzina", "07", "48"},
                {"2026-09-05", "Sopar amb amics", "11", "31.50"}, {"2026-09-09", "Súper", "01", "71.15"},
                {"2026-09-13", "Sabates", "03", "54.90"}, {"2026-09-16", "Farmàcia", "06", "12.30"},
                {"2026-09-20", "Súper", "01", "58.75"}, {"2026-09-24", "Cinema", "09", "16"}};
            String[][] oct = {{"2026-09-29", "Súper", "01", "66.20"}, {"2026-10-03", "Benzina", "07", "45"},
                {"2026-10-06", "Esmorzar", "11", "9.80"}, {"2026-10-10", "Súper", "01", "74.35"},
                {"2026-10-14", "Llibre", "09", "21.90"}, {"2026-10-18", "Sopar d'aniversari", "11", "42"},
                {"2026-10-22", "Súper", "01", "61.05"}, {"2026-10-25", "Detergent i paper", "05", "14.60"}};
            for (var month : java.util.List.of(new Object[]{YearMonth.of(2026, 9), sep, LocalDate.of(2026, 9, 28)},
                    new Object[]{YearMonth.of(2026, 10), oct, LocalDate.of(2026, 10, 28)})) {
                YearMonth key = (YearMonth) month[0];
                LocalDate closeOn = (LocalDate) month[2];
                var calc = cat.pessic.core.budget.BudgetCalculator.of(p);
                for (var sp : calc.planFor(key)) p = cat.pessic.core.payment.PaymentOps.markPaid(p, sp, calc.cycle(key), sp.date());
                for (String[] e : (String[][]) month[1]) {
                    p = cat.pessic.core.expense.ExpenseOps.addMovement(p, LocalDate.parse(e[0]), e[1], Category.ofCode(e[2]),
                            Money.of(e[3]), false);
                }
                if (key.getMonthValue() == 10) {
                    for (var line : calc.annualDue(key, p.movements())) {
                        p = cat.pessic.core.payment.PaymentOps.markAnnualPaid(p, line, calc.cycle(key), LocalDate.of(2026, 10, 12));
                    }
                }
                java.util.Map<String, java.math.BigDecimal> contributions = key.getMonthValue() == 10
                        ? java.util.Map.of(Pot.RESERVE_ID, Money.of("127.23"), trip.id(), Money.of("120"), emergency.id(), Money.of("100"))
                        : java.util.Map.of();
                p = cat.pessic.core.monthclose.MonthClose.close(p, key, contributions,
                        cat.pessic.core.monthclose.CycleClose.Leftover.SAVINGS, null, closeOn);
            }
            p = IncomeOps.addIncome(p, LocalDate.of(2026, 11, 7), "Venda de la bici vella", Money.of("85"), Income.Kind.OTHER,
                    Income.Destination.BUDGET, null, null, null);
            p = IncomeOps.addIncome(p, LocalDate.of(2026, 11, 8), "Samarreta tornada", Money.of("19.95"), Income.Kind.REFUND,
                    Income.Destination.CATEGORY, Category.CLOTHING, null, null);
            p = AccountOps.setAccountBalance(p, Money.of("1186.40"), LocalDate.of(2026, 11, 8));
            repo.save(p);
            System.out.println("demo: " + p.name() + ", " + p.movements().size() + " movements");
        }
    }
}
