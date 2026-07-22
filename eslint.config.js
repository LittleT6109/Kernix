import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    extends: [tseslint.configs.recommended],
    files: ['**/*.ts'],
    languageOptions: {
      parserOptions: {
        project: './tsconfig.json',
      },
    },
    rules: {
      '@typescript-eslint/no-unused-vars': 'error',
    },
  },
  {
    ignores: ['dist/**', 'node_modules/**'],
  }
);
