#!/usr/bin/env node

import { execSync } from 'child_process'
import fs from 'fs'
import path from 'path'

const CONTRACTS_DIR = path.join(process.cwd(), 'src', 'contracts')
const BUILD_DIR = path.join(process.cwd(), 'src', 'contracts')

// Ensure build directory exists
if (!fs.existsSync(BUILD_DIR)) {
  fs.mkdirSync(BUILD_DIR, { recursive: true })
}

// Get all .cash files
const contractFiles = fs.readdirSync(CONTRACTS_DIR).filter((file) => file.endsWith('.cash'))

// Compile each contract
contractFiles.forEach((contractFile) => {
  const contractPath = path.join(CONTRACTS_DIR, contractFile)
  const contractName = path.basename(contractFile, '.cash')
  const outputPath = path.join(BUILD_DIR, `${contractName}.json`)

  try {
    // Run cashc compiler
    const output = execSync(`cashc ${contractPath}`, { encoding: 'utf8' })

    // Parse the output and create JSON artifact
    const artifact = {
      contractName,
      source: fs.readFileSync(contractPath, 'utf8'),
      bytecode: output.trim(),
      abi: [], // You would need to parse the ABI from the compiled output
      updatedAt: new Date().toISOString(),
    }

    // Write the artifact
    fs.writeFileSync(outputPath, JSON.stringify(artifact, null, 2))
  } catch (error) {
    // Only show error if needed for user
  }
})
