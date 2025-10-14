import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

class fib {
    public static int fib(int n) {
        if (n < 2)
            return 1;
        return fib(n - 1) + fib(n - 2);
    }

    public static void main(String[] args) throws Exception {
        int n = 40;
        List<Long> sequence = new ArrayList<>();
        long start = System.nanoTime();

        for (int i = 1; i <= n; i++) {
            long val = fib(i);
            sequence.add(val);
            System.out.println(i + ". fibonacci: " + val);
        }

        double seconds = (System.nanoTime() - start) / 1e9;

        try (PrintWriter out = new PrintWriter("result_java.json")) {
            out.printf("{\n  \"language\": \"Java\",\n  \"n\": %d,\n  \"sequence\": [", n);
            for (int i = 0; i < sequence.size(); i++) {
                out.print(sequence.get(i));
                if (i < sequence.size() - 1)
                    out.print(", ");
            }
            out.printf("],\n  \"seconds\": %.6f\n}\n", seconds);
        }
    }
}
