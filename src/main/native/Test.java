public class Test {
    static {
        System.load("/Users/brunocotrim/IdeaProjects/ArchiveMint/src/main/native/por.so");
    }
    public native boolean nativeMethod(String str1, String str2);
    public static void main(String[] args) {
        System.out.println("Hello World!");
        Test test = new Test();
        System.out.println(test.nativeMethod("0000000000000000000000000000000000000000000000000000000000000000", "3b9d89bc8ae0c8b0c28ea6616151ce07c140f4ac7286b379736c7935d857a80d7c9189f2b1dad9f1eebcb66e2e3ce425fd6fde9e52f4dc4348464f04a65aa95518f4efd2ee85ae909dd1e931241f8d4b9e03abfa37d4e0303c22266ad274c16b643adbb06a68d1dd3d399b20853ceca318136837a7aa92d1da81c52d4b0342b9a9b1aad77595d9bff2491464c9c4212d6967cafb3eb58029376d703721aaf31b94c3419f8f11288bb312095346a5a5ea9b6e65545f20d314f4c1ca68f4440f7d5c4cc26de15f156b217fc94d292f3a24692ae36f654555fc09ee6e7270b9153e0e0c8761f9891a28d4673988434d3ceaaded9002e89aad2267f5f7b879be4cee"));
    }
}