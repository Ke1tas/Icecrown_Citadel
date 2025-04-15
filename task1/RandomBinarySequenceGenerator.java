import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

public class RandomBinarySequenceGenerator {
    public static void main(String[] args) {
        int length = 128;
        StringBuilder binarySequence = new StringBuilder();
        Random random = new Random();

        for (int i = 0; i < length; i++) {
            int bit = random.nextInt(2);
            binarySequence.append(bit);
        }

        try (BufferedWriter writer = new BufferedWriter(new FileWriter("binary_sequence_java.txt"))) {
            writer.write(binarySequence.toString());
            System.out.println("Случайная бинарная последовательность записана в файл random_binary_sequence_java.txt");
        } catch (IOException e) {
            System.err.println("Ошибка при записи в файл: " + e.getMessage());
        }
    }
}